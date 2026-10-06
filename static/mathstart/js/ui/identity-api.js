/* MS7-I03 frozen HTTP consumer. No browser storage or client-owned knowledge state. */
(function (root, factory) {
  "use strict";
  const exported = factory();
  if (typeof module === "object" && module.exports) module.exports = exported;
  else root.MathStartIdentity = exported;
})(globalThis, function () {
  "use strict";
  const routes = Object.freeze({
    register: ["POST", "/api/v1/auth/register/", true],
    login: ["POST", "/api/v1/auth/login/", false],
    logout: ["POST", "/api/v1/auth/logout/", false],
    profile: ["PATCH", "/api/v1/users/me/", false],
    onboarding: ["POST", "/api/v1/onboarding/complete/", true]
  });
  const modes = ["START_ZERO", "SELF_REPORT", "DIAGNOSTIC"];
  class APIError extends Error {
    constructor(code, status = 0, retryable = false, fieldErrors = {}, retryAfter = 0) {
      super(code);
      this.code = code;
      this.status = status;
      this.retryable = retryable;
      this.fieldErrors = fieldErrors;
      this.retryAfter = retryAfter;
    }
  }
  const invalidResponse = () => new APIError("INVALID_RESPONSE", 0, true);
  const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
  const id = value => (typeof value === "number" && Number.isSafeInteger(value) && value > 0)
    || (typeof value === "string" && /^[0-9]{1,19}$/.test(value) && /[1-9]/.test(value));
  function user(body) {
    const data = body && body.data;
    if (!object(data) || Object.keys(data).sort().join(",") !==
        "id,onboarding_complete,onboarding_mode,selected_grade_id,username" || !id(data.id)
        || typeof data.username !== "string" || !data.username
        || (data.selected_grade_id !== null && !id(data.selected_grade_id))
        || (data.onboarding_mode !== null && !modes.includes(data.onboarding_mode))
        || typeof data.onboarding_complete !== "boolean") throw invalidResponse();
    return data;
  }
  function actionKey() {
    const bytes = new Uint8Array(16);
    globalThis.crypto.getRandomValues(bytes);
    return "i03-" + Array.from(bytes, byte => byte.toString(16).padStart(2, "0")).join("");
  }
  function createClient({fetch: fetcher = globalThis.fetch.bind(globalThis),
    keyFactory = actionKey, timeout = 20000} = {}) {
    async function request(path, options = {}) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeout);
      try {
        let response;
        try {
          response = await fetcher(path, {...options, credentials: "same-origin",
            cache: "no-store", redirect: "error", signal: controller.signal});
        } catch (_) { throw new APIError("NETWORK_ERROR", 0, true); }
        let body;
        try { body = await response.json(); } catch (_) { throw invalidResponse(); }
        if (!response.ok) {
          const error = body && body.error;
          const fields = object(error && error.field_errors) ? error.field_errors : {};
          const seconds = Number(response.headers.get("Retry-After"));
          throw new APIError(typeof (error && error.code) === "string" ? error.code : "INVALID_RESPONSE",
            response.status, Boolean(error && error.retryable), fields,
            Number.isFinite(seconds) && seconds > 0 ? Math.ceil(seconds) : 0);
        }
        if (!object(body) || !object(body.meta) || typeof body.meta.request_id !== "string"
            || (body.meta.version !== undefined && body.meta.version !== "http-v1")) throw invalidResponse();
        return body;
      } finally { clearTimeout(timer); }
    }
    async function csrf() {
      const body = await request("/api/v1/auth/csrf/");
      if (!object(body.data) || typeof body.data.csrf_token !== "string" || !body.data.csrf_token) throw invalidResponse();
      return body.data.csrf_token;
    }
    async function me() {
      try { return user(await request("/api/v1/users/me/")); }
      catch (error) { if (error.status === 401) return null; throw error; }
    }
    function action(name, payload) {
      if (!Object.hasOwn(routes, name)) throw new Error("Unsupported identity operation");
      const [method, path, receipt] = routes[name];
      // Serialize once: retries cannot pick up subsequently edited form values.
      return Object.freeze({name, method, path, body: JSON.stringify(payload),
        key: receipt ? keyFactory() : null});
    }
    async function send(operation) {
      // A fresh bootstrap for every mutation also handles login/registration rotation.
      const token = await csrf();
      const headers = {"Content-Type": "application/json", "X-CSRFToken": token};
      if (operation.key) headers["Idempotency-Key"] = operation.key;
      const body = await request(operation.path, {method: operation.method, headers, body: operation.body});
      if (operation.name === "logout") {
        if (!object(body.data) || body.data.completed !== true) throw invalidResponse();
        return null;
      }
      return user(body);
    }
    async function grades(pageSize = 20) {
      const rows = [], identities = new Set(), cursors = new Set();
      let cursor = null;
      do {
        const query = new URLSearchParams({page_size: String(pageSize)});
        if (cursor !== null) query.set("cursor", cursor);
        const body = await request("/api/v1/grades/?" + query);
        const page = body.meta.pagination;
        if (!Array.isArray(body.data) || !object(page) || page.page_size !== pageSize
            || typeof page.has_more !== "boolean"
            || (page.has_more ? typeof page.next_cursor !== "string" || !page.next_cursor : page.next_cursor !== null)) {
          throw invalidResponse();
        }
        for (const row of body.data) {
          if (!object(row) || Object.keys(row).sort().join(",") !== "id,number,title" || !id(row.id)
              || !Number.isInteger(row.number) || row.number < 1 || row.number > 12
              || typeof row.title !== "string" || !row.title || identities.has(String(row.id))) throw invalidResponse();
          identities.add(String(row.id));
          rows.push(row);
        }
        cursor = page.next_cursor;
        if (cursor !== null) {
          if (cursors.has(cursor)) throw invalidResponse();
          cursors.add(cursor);
        }
      } while (cursor !== null);
      return rows;
    }
    return Object.freeze({csrf, me, action, send, grades});
  }
  return {APIError, createClient};
});
