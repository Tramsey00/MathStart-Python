/* Production JS transport against Django's isolated live test server, no browser. */
"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const {createClient} = require("../static/mathstart/js/ui/identity-api.js");
const base = process.env.MATHSTART_I03_TEST_URL;
if (!base || !/^http:\/\/localhost:\d+$/.test(base)) throw new Error("Isolated Django live server required");
const password = "Synthetic-I03-Test-Only-47!";
function browserTransport() {
  const cookies = new Map();
  const fault = {dropPath: null};
  async function fetcher(path, options = {}) {
    const headers = new Headers(options.headers);
    if (cookies.size) headers.set("Cookie", [...cookies].map(([name, value]) => `${name}=${value}`).join("; "));
    if (options.method) headers.set("Origin", base);
    const response = await fetch(base + path, {...options, headers});
    for (const cookie of response.headers.getSetCookie()) {
      const pair = cookie.split(";", 1)[0], index = pair.indexOf("=");
      const name = pair.slice(0, index), value = pair.slice(index + 1);
      if (value) cookies.set(name, value); else cookies.delete(name);
    }
    if (options.method && path === fault.dropPath && response.ok) {
      fault.dropPath = null;
      await response.arrayBuffer(); // Server committed; only the acknowledgement is lost.
      throw new Error("synthetic lost acknowledgement");
    }
    return response;
  }
  return {cookies, fetcher, fault, client: createClient({fetch: fetcher})};
}

test("production transport: registration, real grade ids/pages, PATCH, three modes/replay, login saved-state and logout", async () => {
  const {client, cookies, fetcher, fault} = browserTransport();
  assert.equal(await client.me(), null);
  const bootstrap = await client.csrf();
  const originalCookie = cookies.get("csrftoken");
  const register = client.action("register", {username: "i03-runtime-student", password});
  fault.dropPath = "/api/v1/auth/register/";
  await assert.rejects(client.send(register), {code: "NETWORK_ERROR"});
  const registered = await client.send(register);
  assert.equal(registered.username, "i03-runtime-student");
  assert.equal(registered.onboarding_complete, false);
  assert.notEqual(cookies.get("csrftoken"), originalCookie);
  assert.deepEqual(await client.send(register), registered);
  const rejected = await fetcher("/api/v1/users/me/", {method: "PATCH",
    headers: {"Content-Type": "application/json", "X-CSRFToken": bootstrap}, body: JSON.stringify({selected_grade_id: 70})});
  assert.equal(rejected.status, 403); // Old token after registration cannot authorize a mutation.
  const grades = await client.grades(1); // Actual signed multi-page cursor flow.
  assert.equal(grades.length, 3);
  const grade = grades.find(row => row.number === 5);
  assert.notEqual(grade.id, grade.number);
  await client.send(client.action("profile", {selected_grade_id: grade.id}));
  assert.equal((await client.me()).selected_grade_id, grade.id);
  for (const mode of ["START_ZERO", "SELF_REPORT", "DIAGNOSTIC"]) {
    const operation = client.action("onboarding", {selected_grade_id: grade.id, mode});
    if (mode === "SELF_REPORT") {
      fault.dropPath = "/api/v1/onboarding/complete/";
      await assert.rejects(client.send(operation), {code: "NETWORK_ERROR"});
    }
    const first = await client.send(operation);
    const replay = await client.send(operation);
    assert.deepEqual(replay, first);
    assert.equal(first.onboarding_mode, mode);
    assert.equal(first.onboarding_complete, true);
    assert.deepEqual(await client.me(), first);
    if (mode === "SELF_REPORT") {
      const changed = {...operation, body: JSON.stringify({selected_grade_id: grade.id, mode: "START_ZERO"})};
      await assert.rejects(client.send(changed), {status: 409, code: "IDEMPOTENCY_CONFLICT"});
    }
  }
  const beforeLogout = await client.me();
  await client.send(client.action("logout", {}));
  assert.equal(await client.me(), null);
  await assert.rejects(client.send(client.action("logout", {})), {status: 401});
  await client.send(client.action("login", {username: "i03-runtime-student", password}));
  assert.deepEqual(await client.me(), beforeLogout);
  const {client: restored} = {client: createClient({fetch: fetcher})}; // New controller/client; no local profile cache.
  assert.deepEqual(await restored.me(), beforeLogout);
});

test("production transport: missing, wrong and inactive credentials have indistinguishable safe errors", async () => {
  const {client} = browserTransport();
  const outcomes = [];
  for (const [username, supplied] of [["i03-missing", password], ["i03-runtime-student", "wrong-synthetic"], ["i03-inactive", password]]) {
    try { await client.send(client.action("login", {username, password: supplied})); assert.fail("must fail"); }
    catch (error) { outcomes.push([error.status, error.code, error.message, error.fieldErrors]); }
  }
  assert.deepEqual(outcomes[0], [401, "AUTHENTICATION_REQUIRED", "AUTHENTICATION_REQUIRED", {}]);
  assert.deepEqual(outcomes[1], outcomes[0]); assert.deepEqual(outcomes[2], outcomes[0]);
  assert.equal(await client.me(), null);
});

test("anonymous registration requires a real CSRF header; public grades require none", async () => {
  const {client, fetcher} = browserTransport();
  const before = await client.grades();
  assert.equal(before.length, 3);
  await client.csrf();
  const response = await fetcher("/api/v1/auth/register/", {method: "POST", headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username: "i03-no-csrf", password})});
  assert.equal(response.status, 403);
  assert.equal((await response.json()).error.code, "CSRF_FAILED");
  assert.equal(await client.me(), null);
});
