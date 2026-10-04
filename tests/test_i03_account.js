/* Production controller tests with a minimal DOM adapter, not browser acceptance. */
"use strict";
const {test} = require("node:test");
const assert = require("node:assert/strict");
const {mount} = require("../static/mathstart/js/ui/account.js");
const {createClient} = require("../static/mathstart/js/ui/identity-api.js");
function documentAdapter() {
  const nodes = new Map();
  const doc = {activeElement: null, getElementById: id => nodes.get(id) || null,
    createElement: () => node("")};
  function node(id) {
    const item = {id, value: "", textContent: "", hidden: false, disabled: false, checked: false,
      dataset: {}, attrs: {}, children: [], events: {}, fields: [], valid: true,
      setAttribute(name, value) { this.attrs[name] = value; },
      addEventListener(name, callback) { this.events[name] = callback; },
      async emit(name) { let prevented = false; await this.events[name]({preventDefault() { prevented = true; }}); return prevented; },
      reportValidity() { return this.valid; }, querySelector() { return this.fieldset; },
      querySelectorAll() { return this.fields; },
      replaceChildren() { this.children = []; }, append(child) { this.children.push(child); },
      focus() {
        // Native controls cannot receive focus inside a disabled fieldset.
        if (!this.disabled && !this.parentFieldset?.disabled) doc.activeElement = this;
      }
    };
    // Any regression to an unsafe HTML sink is a test failure.
    Object.defineProperty(item, "innerHTML", {set() { throw new Error("unsafe HTML sink"); }});
    if (id) nodes.set(id, item);
    return item;
  }
  for (const id of ["account-main", "account-state", "account-status", "account-error", "account-retry", "account-refresh",
    "anonymous-panel", "profile-panel", "profile-title", "saved-username", "saved-grade", "saved-mode", "saved-completion",
    "grades-status", "grades-error", "grades-retry", "onboarding-mode"]) node(id);
  for (const name of ["register", "login", "profile", "onboarding", "logout"]) {
    const form = node(name + "-form"); form.fieldset = node(""); node(name + "-error");
    const fields = name === "register" ? ["username", "password", "email"] : name === "login" ? ["username", "password"]
      : ["profile", "onboarding"].includes(name) ? ["grade"] : [];
    for (const field of fields) {
      const input = node(name + "-" + field);
      input.parentFieldset = form.fieldset;
      form.fields.push(input);
      node(name + "-" + field + "-error");
    }
  }
  for (const [id, mode] of [["mode-start-zero", "START_ZERO"], ["mode-self-report", "SELF_REPORT"], ["mode-diagnostic", "DIAGNOSTIC"]]) node(id).value = mode;
  return doc;
}
function fixture(initial = null, options = {}) {
  const doc = documentAdapter(), requests = [], receipts = new Map();
  const state = {profile: initial, lost: null, failGrades: false, loginFailure: false, rotate: 0, ...options};
  let keys = 0;
  const response = (data, status = 200) => ({ok: status < 400, status, headers: new Headers(),
    json: async () => status < 400 ? {data, meta: {request_id: "synthetic", version: "http-v1"}}
      : {error: {code: "AUTHENTICATION_REQUIRED", message: "Invalid username or password.", field_errors: {}, retryable: false, request_id: "synthetic"}}});
  const client = createClient({keyFactory: () => "logical-" + ++keys, fetch: async (path, options) => {
    requests.push({path, ...options});
    if (path.endsWith("csrf/")) {
      state.rotate++;
      if (state.rotate === state.failCSRFAt) throw new Error("csrf bootstrap temporarily unavailable");
      return response({csrf_token: "token-" + state.rotate});
    }
    if (path.includes("/grades/")) {
      if (state.failGrades) throw new Error("offline");
      const body = {data: [{id: 70, number: 5, title: "<b>5 класс</b>"}],
        meta: {request_id: "synthetic", pagination: {page_size: 20, has_more: false, next_cursor: null}}};
      return {ok: true, status: 200, headers: new Headers(), json: async () => body};
    }
    if (!options.method) {
      if (state.failMe) throw new Error("saved-state read temporarily unavailable");
      return response(state.profile, state.profile ? 200 : 401);
    }
    const body = JSON.parse(options.body);
    const key = options.headers["Idempotency-Key"];
    if (key && receipts.has(key)) return response(receipts.get(key));
    if (path.endsWith("login/") && state.loginFailure) return response(null, 401);
    if (path.endsWith("register/") || path.endsWith("login/")) state.profile = {id: 1, username: body.username,
      selected_grade_id: null, onboarding_mode: null, onboarding_complete: false};
    else if (path.endsWith("logout/")) state.profile = null;
    else if (path.endsWith("onboarding/complete/")) state.profile = {...state.profile, selected_grade_id: body.selected_grade_id, onboarding_mode: body.mode, onboarding_complete: true};
    else state.profile = {...state.profile, selected_grade_id: body.selected_grade_id};
    if (key) receipts.set(key, {...state.profile});
    if (state.lost === path) { state.lost = null; throw new Error("lost acknowledgement"); }
    return response(path.endsWith("logout/") ? {completed: true} : state.profile);
  }});
  const app = mount({document: doc, client});
  return {doc, state, requests, app, el: name => doc.getElementById(name)};
}
const saved = {id: 1, username: "<img src=x>", selected_grade_id: 70, onboarding_mode: "DIAGNOSTIC", onboarding_complete: true};

test("ordinary anonymous initial state loads automatically without a recovery button", async () => {
  const f = fixture(); await f.app.ready;
  assert.equal(f.el("anonymous-panel").hidden, false);
  assert.equal(f.el("account-refresh").hidden, true);
  assert.equal(f.el("login-form").fieldset.disabled, false);
  assert.equal(f.requests.filter(r => r.path === "/api/v1/users/me/").length, 1);
});

test("failed state loading offers GET-me-only recovery; repeated failure remains keyboard reachable", async () => {
  const f = fixture(null, {failMe: true}); await f.app.ready;
  assert.equal(f.el("account-refresh").hidden, false);
  assert.equal(f.el("login-form").fieldset.disabled, true);
  assert.equal(f.el("account-status").textContent, "Не удалось загрузить сохранённое состояние.");
  await f.el("account-refresh").emit("click");
  assert.equal(f.el("account-refresh").hidden, false);
  assert.equal(f.el("account-status").textContent, "Не удалось загрузить сохранённое состояние.");
  assert.equal(f.el("account-refresh").disabled, false);
  assert.equal(f.doc.activeElement.id, "account-error");
  f.state.failMe = false;
  await f.el("account-refresh").emit("click");
  assert.equal(f.el("account-refresh").hidden, true);
  assert.equal(f.el("anonymous-panel").hidden, false);
  assert.equal(f.doc.activeElement.id, "login-username");
  assert.equal(f.requests.filter(r => r.path === "/api/v1/users/me/").length, 3);
  assert.equal(f.requests.filter(r => r.method).length, 0);
  assert.equal(f.state.rotate, 1); // Recovery reads GET me; no auth/CSRF mutation replay.
});

test("successful authenticated recovery hides retry and restores saved state with usable focus", async () => {
  const f = fixture(saved, {failMe: true}); await f.app.ready;
  f.state.failMe = false;
  await f.el("account-refresh").emit("click");
  assert.equal(f.el("saved-username").textContent, saved.username);
  assert.equal(f.el("profile-grade").value, "70");
  assert.equal(f.el("mode-diagnostic").checked, true);
  assert.equal(f.el("account-refresh").hidden, true);
  assert.equal(f.doc.activeElement.id, "profile-title");
});

test("saved state restores through real consumer reads and escaped text sinks, with returned grade identity", async () => {
  const f = fixture(saved); await f.app.ready;
  assert.equal(f.el("saved-username").textContent, saved.username);
  assert.equal(f.el("saved-grade").textContent, "<b>5 класс</b>");
  assert.equal(f.el("profile-grade").value, "70");
  assert.equal(f.el("mode-diagnostic").checked, true);
  assert.equal(f.el("saved-completion").textContent, "Настройка сохранена");
  assert.equal(f.el("profile-form").fieldset.disabled, false);
  assert.equal(f.el("account-refresh").hidden, true);
  assert.ok(f.requests.some(r => r.path === "/api/v1/users/me/"));
});

test("native submit constructs exact registration payload, omits blank email and restores after rotation", async () => {
  const f = fixture(); await f.app.ready;
  f.el("register-username").value = "synthetic"; f.el("register-password").value = "synthetic-only";
  assert.equal(await f.el("register-form").emit("submit"), true);
  const post = f.requests.find(r => r.path.endsWith("register/") && r.method);
  assert.deepEqual(JSON.parse(post.body), {username: "synthetic", password: "synthetic-only"});
  assert.equal(f.el("register-password").value, "");
  assert.equal(f.el("anonymous-panel").hidden, true);
  assert.equal(f.doc.activeElement.id, "profile-title");
  assert.ok(f.state.rotate >= 3);
});

test("all three mode forms send returned id, mode only, and a distinct key for a new operation", async () => {
  const f = fixture({...saved, onboarding_mode: null, onboarding_complete: false}); await f.app.ready;
  const keys = new Set();
  for (const [id, mode] of [["mode-start-zero", "START_ZERO"], ["mode-self-report", "SELF_REPORT"], ["mode-diagnostic", "DIAGNOSTIC"]]) {
    for (const radio of ["mode-start-zero", "mode-self-report", "mode-diagnostic"]) f.el(radio).checked = radio === id;
    f.el("onboarding-grade").value = "70";
    await f.el("onboarding-form").emit("submit");
    const post = f.requests.filter(r => r.path.endsWith("complete/") && r.method).at(-1);
    assert.deepEqual(JSON.parse(post.body), {selected_grade_id: 70, mode});
    keys.add(post.headers["Idempotency-Key"]);
    assert.equal(f.el(id).checked, true);
  }
  assert.equal(keys.size, 3);
});

test("SELF_REPORT lost acknowledgement freezes the action and uses identical body/key on explicit retry", async () => {
  const f = fixture({...saved, onboarding_mode: "SELF_REPORT"}); await f.app.ready;
  f.state.lost = "/api/v1/onboarding/complete/";
  await f.el("onboarding-form").emit("submit");
  assert.equal(f.el("account-retry").hidden, false);
  assert.equal(f.el("onboarding-form").fieldset.disabled, true);
  assert.equal(f.doc.activeElement.id, "account-error");
  f.el("onboarding-grade").value = "5"; // A programmatic edit cannot alter the frozen action.
  await f.el("onboarding-form").emit("submit");
  await f.el("account-retry").emit("click");
  const posts = f.requests.filter(r => r.path.endsWith("complete/") && r.method);
  assert.equal(posts.length, 2);
  assert.equal(posts[0].body, posts[1].body);
  assert.equal(posts[0].headers["Idempotency-Key"], posts[1].headers["Idempotency-Key"]);
  assert.equal(f.el("account-retry").hidden, true);
  assert.equal(f.el("account-refresh").hidden, true);
  assert.equal(f.el("onboarding-grade").value, "70");
});

test("safe invalid credentials stay form-level; successful login/logout restores focus and state", async () => {
  const f = fixture(); await f.app.ready;
  f.el("login-username").value = "synthetic"; f.el("login-password").value = "synthetic-only";
  f.state.loginFailure = true;
  await f.el("login-form").emit("submit");
  assert.equal(f.el("login-error").textContent, "Не удалось войти. Проверьте имя пользователя и пароль.");
  assert.equal(f.el("account-retry").hidden, true);
  f.state.loginFailure = false;
  await f.el("login-form").emit("submit");
  await f.el("logout-form").emit("submit");
  assert.equal(f.el("anonymous-panel").hidden, false);
  assert.equal(f.doc.activeElement.id, "login-username");
  assert.equal(f.el("saved-username").textContent, "");
});

test("grade failure is not successful empty state; retry restores catalogue controls", async () => {
  const f = fixture(saved, {failGrades: true}); await f.app.ready;
  assert.equal(f.el("grades-error").hidden, false);
  assert.equal(f.el("profile-form").fieldset.disabled, true);
  assert.equal(f.el("grades-status").textContent, "Список классов не загружен.");
  f.state.failGrades = false; await f.el("grades-retry").emit("click");
  assert.equal(f.el("profile-form").fieldset.disabled, false);
});

test("an owner change during pending retry stops before another account mutation", async () => {
  const f = fixture(saved); await f.app.ready;
  f.state.lost = "/api/v1/onboarding/complete/";
  await f.el("onboarding-form").emit("submit");
  f.state.profile = {...saved, id: 2, username: "other-synthetic"};
  await f.el("account-retry").emit("click");
  assert.equal(f.requests.filter(r => r.path.endsWith("complete/") && r.method).length, 1);
  assert.ok(f.el("account-error").textContent.startsWith("Сеанс изменился"));
});

test("native validity prevents a request without bypassing semantic form submission", async () => {
  const f = fixture(); await f.app.ready;
  f.el("register-form").valid = false;
  await f.el("register-form").emit("submit");
  assert.equal(f.requests.filter(r => r.method).length, 0);
});

test("known auth acknowledgement with failed CSRF refresh suspends forms and recovers through GET me without resubmission", async () => {
  const f = fixture(null, {failCSRFAt: 3}); await f.app.ready;
  f.el("register-username").value = "synthetic"; f.el("register-password").value = "synthetic-only";
  await f.el("register-form").emit("submit");
  assert.equal(f.el("account-retry").hidden, true);
  assert.equal(f.el("register-form").fieldset.disabled, true);
  assert.equal(f.el("anonymous-panel").hidden, true);
  assert.equal(f.el("account-main").attrs["aria-busy"], "false");
  assert.equal(f.el("account-refresh").hidden, false);
  await f.el("account-refresh").emit("click");
  assert.equal(f.el("profile-panel").hidden, false);
  assert.equal(f.el("saved-username").textContent, "synthetic");
  assert.equal(f.el("account-refresh").hidden, true);
  assert.equal(f.doc.activeElement.id, "profile-title");
  assert.equal(f.requests.filter(r => r.path.endsWith("register/") && r.method).length, 1);
});

test("lost login/logout acknowledgements reconcile saved session state before any non-idempotent resubmission", async () => {
  const f = fixture(); await f.app.ready;
  f.el("login-username").value = "synthetic"; f.el("login-password").value = "synthetic-only";
  f.state.lost = "/api/v1/auth/login/";
  await f.el("login-form").emit("submit");
  await f.el("account-retry").emit("click");
  assert.equal(f.requests.filter(r => r.path.endsWith("login/") && r.method).length, 1);
  f.state.lost = "/api/v1/auth/logout/";
  await f.el("logout-form").emit("submit");
  await f.el("account-retry").emit("click");
  assert.equal(f.requests.filter(r => r.path.endsWith("logout/") && r.method).length, 1);
  assert.equal(f.el("anonymous-panel").hidden, false);
});

test("historical onboarding response does not replace current server profile", async () => {
  const f = fixture({...saved, onboarding_mode: "SELF_REPORT"}); await f.app.ready;
  f.state.lost = "/api/v1/onboarding/complete/";
  await f.el("onboarding-form").emit("submit");
  f.state.profile = {...f.state.profile, onboarding_mode: "START_ZERO"};
  // Mutation retry still reads current GET me after the historical receipt.
  assert.equal(f.el("account-refresh").hidden, true);
  assert.equal(f.el("account-retry").hidden, false);
  await f.el("account-retry").emit("click"); // Receipt still returns SELF_REPORT, current GET me returns START_ZERO.
  assert.equal(f.el("saved-mode").textContent, "Начать с начала");
  assert.equal(f.el("mode-start-zero").checked, true);
  assert.equal(f.el("account-retry").hidden, true);
});
