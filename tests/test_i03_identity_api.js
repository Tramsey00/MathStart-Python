/* Targeted production transport tests; Node only, no npm/browser toolchain. */
"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const {createClient} = require("../static/mathstart/js/ui/identity-api.js");
const profile = {id: 1, username: "synthetic", selected_grade_id: 70,
  onboarding_mode: "SELF_REPORT", onboarding_complete: true};
const reply = (data, status = 200, headers = {}) => ({ok: status < 400, status,
  headers: new Headers(headers), json: async () => ({data, meta: {request_id: "synthetic", version: "http-v1"}})});
const failure = (status, code, retryable = false, headers = {}) => ({ok: false, status,
  headers: new Headers(headers), json: async () => ({error: {code, message: "safe", field_errors: {}, retryable, request_id: "synthetic"}})});
function harness(responder) {
  const requests = [];
  let keys = 0, tokens = 0;
  const client = createClient({keyFactory: () => "key-" + ++keys, fetch: async (path, options) => {
    requests.push({path, ...options});
    if (path.endsWith("auth/csrf/")) return reply({csrf_token: "token-" + ++tokens});
    return responder(path, options);
  }});
  return {client, requests};
}

test("anonymous register and login use CSRF and same-origin JSON; rotation never reuses a token", async () => {
  const {client, requests} = harness(() => reply(profile));
  await client.send(client.action("register", {username: "synthetic", password: "synthetic-only"}));
  await client.csrf(); // Successful auth recovery obtains the rotated token.
  await client.send(client.action("login", {username: "synthetic", password: "synthetic-only"}));
  const posts = requests.filter(r => r.method === "POST");
  assert.equal(posts[0].headers["X-CSRFToken"], "token-1");
  assert.equal(posts[1].headers["X-CSRFToken"], "token-3");
  assert.equal(posts[0].headers["Idempotency-Key"], "key-1");
  assert.equal(posts[1].headers["Idempotency-Key"], undefined);
  for (const request of posts) {
    assert.equal(request.credentials, "same-origin");
    assert.equal(request.headers["Content-Type"], "application/json");
    assert.equal(request.redirect, "error");
  }
});

test("lost acknowledgement retries frozen payload/key; explicit new action gets a new key", async () => {
  let calls = 0;
  const {client, requests} = harness(() => {
    if (++calls === 1) throw new Error("lost acknowledgement");
    return reply(profile);
  });
  const payload = {selected_grade_id: 70, mode: "SELF_REPORT"};
  const operation = client.action("onboarding", payload);
  payload.selected_grade_id = 5;
  await assert.rejects(client.send(operation), {code: "NETWORK_ERROR", retryable: true});
  await client.send(operation);
  const posts = requests.filter(r => r.method === "POST");
  assert.equal(posts[0].body, posts[1].body);
  assert.equal(posts[0].headers["Idempotency-Key"], posts[1].headers["Idempotency-Key"]);
  assert.deepEqual(JSON.parse(posts[1].body), {selected_grade_id: 70, mode: "SELF_REPORT"});
  assert.notEqual(client.action("onboarding", payload).key, operation.key);
});

test("grade pagination retains returned IDs and opaque encoded cursors with unchanged page size", async () => {
  const {client, requests} = harness(path => {
    const cursor = new URL(path, "https://example.invalid").searchParams.get("cursor");
    return {ok: true, status: 200, headers: new Headers(), json: async () => ({
      data: cursor ? [{id: 50, number: 6, title: "6 класс"}] : [{id: 70, number: 5, title: "5 класс"}],
      meta: {request_id: "synthetic", pagination: {page_size: 1, has_more: !cursor, next_cursor: cursor ? null : "opaque:+/&="}}
    })};
  });
  assert.deepEqual(await client.grades(1), [{id: 70, number: 5, title: "5 класс"}, {id: 50, number: 6, title: "6 класс"}]);
  const query = new URL(requests[1].path, "https://example.invalid").searchParams;
  assert.equal(query.get("cursor"), "opaque:+/&=");
  assert.equal(query.get("page_size"), "1");
  assert.equal(requests[0].headers, undefined);
});

test("empty catalogue is success; malformed/looping/duplicate pagination fails instead of partial success", async () => {
  for (const kind of ["empty", "loop", "duplicate", "missing-cursor", "unsafe-id"]) {
    const {client} = harness(() => ({ok: true, status: 200, headers: new Headers(), json: async () => ({
      data: kind === "empty" ? [] : [{id: kind === "unsafe-id" ? 2 ** 54 : 70, number: 5, title: "5 класс"}],
      meta: {request_id: "synthetic", pagination: {page_size: 20, has_more: kind !== "empty" && kind !== "unsafe-id",
        next_cursor: ["empty", "missing-cursor", "unsafe-id"].includes(kind) ? null : "cursor"}}
    })}));
    if (kind === "empty") assert.deepEqual(await client.grades(), []);
    else await assert.rejects(client.grades(), {code: "INVALID_RESPONSE"});
  }
});

test("private 401 means anonymous; service failure never becomes an empty profile", async () => {
  assert.equal(await harness(() => failure(401, "AUTHENTICATION_REQUIRED")).client.me(), null);
  await assert.rejects(harness(() => failure(503, "SERVICE_UNAVAILABLE", true)).client.me(), {status: 503});
});

test("safe error codes and Retry-After are consumed without exposing server messages", async () => {
  const {client} = harness(() => failure(429, "RATE_LIMITED", true, {"Retry-After": "12"}));
  await assert.rejects(client.send(client.action("login", {username: "synthetic", password: "synthetic-only"})), error => {
    assert.equal(error.message, "RATE_LIMITED");
    assert.equal(error.retryAfter, 12);
    assert.deepEqual(error.fieldErrors, {});
    return true;
  });
});

test("logout and profile update have no receipt header; invalid success cannot confirm a save", async () => {
  const {client, requests} = harness(path => reply(path.endsWith("logout/") ? {completed: true} : profile));
  await client.send(client.action("logout", {}));
  await client.send(client.action("profile", {selected_grade_id: 70}));
  for (const request of requests.filter(r => r.method)) assert.equal(request.headers["Idempotency-Key"], undefined);
  await assert.rejects(harness(() => reply({})).client.send(client.action("profile", {selected_grade_id: 70})), {code: "INVALID_RESPONSE"});
});

test("timeout is an uncertain network failure and does not silently start a second mutation", async () => {
  let count = 0;
  const client = createClient({timeout: 10, fetch: async (path, options) => {
    if (path.endsWith("csrf/")) return reply({csrf_token: "synthetic"});
    count++;
    return new Promise((resolve, reject) => options.signal.addEventListener("abort", () => reject(new Error("timeout"))));
  }});
  await assert.rejects(client.send(client.action("onboarding", {selected_grade_id: 70, mode: "SELF_REPORT"})), {code: "NETWORK_ERROR"});
  assert.equal(count, 1);
});
