/* MS7-I03 presentation. Saved state always comes from GET users/me. */
(function (root, factory) {
  "use strict";
  const exported = factory();
  if (typeof module === "object" && module.exports) module.exports = exported;
  else {
    root.MathStartAccount = exported;
    if (root.document.getElementById("account-main")) {
      exported.mount({document: root.document, client: root.MathStartIdentity.createClient()});
    }
  }
})(globalThis, function () {
  "use strict";
  const modeLabels = {START_ZERO: "Начать с начала", SELF_REPORT: "Самооценка", DIAGNOSTIC: "Диагностика (выбор пути)"};
  const radioIds = ["mode-start-zero", "mode-self-report", "mode-diagnostic"];
  const formNames = ["register", "login", "logout", "profile", "onboarding"];
  const usernameLimitMessage = "Имя пользователя должно содержать не больше 30 символов.";
  function mount({document: doc, client}) {
    const el = name => doc.getElementById(name);
    const forms = Object.fromEntries(formNames.map(name => [name, el(name + "-form")]));
    let profile = null, sessionReady = false, catalogue = [], gradesReady = false;
    let stateReloadNeeded = false;
    let authMode = "login";
    let busy = false, gradesLoading = false, pending = null, retryAt = 0, retryTimer = null;
    const selects = [el("profile-grade"), el("onboarding-grade")];
    const value = name => el(name).value;
    const selectedID = name => {
      const row = catalogue.find(item => String(item.id) === value(name));
      if (!gradesReady || !row) throw new Error("Select a catalogue grade");
      return row.id;
    };
    function controls() {
      for (const [name, form] of Object.entries(forms)) {
        form.querySelector("fieldset").disabled = busy || Boolean(pending) || !sessionReady
          || (["login", "register"].includes(name) && name !== authMode)
          || (["profile", "onboarding"].includes(name) && (!gradesReady || !catalogue.length));
        form.setAttribute("aria-busy", String(busy));
      }
      el("account-main").setAttribute("aria-busy", String(busy));
      el("account-retry").hidden = !pending;
      el("account-retry").disabled = busy || Date.now() < retryAt;
      el("account-refresh").disabled = busy;
      el("account-refresh").hidden = !stateReloadNeeded;
      el("grades-retry").disabled = busy || gradesLoading || Boolean(pending);
      for (const name of ["login", "register"]) el("auth-" + name).disabled = busy || Boolean(pending) || !sessionReady;
    }
    function renderAuth() {
      el("login").hidden = authMode !== "login";
      el("registration").hidden = authMode !== "register";
      for (const name of ["login", "register"]) el("auth-" + name).setAttribute("aria-pressed", String(name === authMode));
    }
    function announce(message, state = "ordinary") {
      el("account-state").hidden = !message;
      el("account-state").dataset.state = state;
      el("account-status").textContent = message;
    }
    function clearErrors() {
      el("account-error").hidden = true;
      el("account-error").textContent = "";
      if (!el("account-status").textContent) el("account-state").hidden = true;
      for (const [name, form] of Object.entries(forms)) {
        el(name + "-error").hidden = true;
        el(name + "-error").textContent = "";
        for (const field of form.querySelectorAll('[aria-invalid]')) {
          field.setAttribute("aria-invalid", "false");
          const error = el(field.id + "-error");
          if (error) { error.hidden = true; error.textContent = ""; }
        }
      }
    }
    function errorMessage(error, name) {
      if (name === "register" && error.code === "USERNAME_TOO_LONG") return usernameLimitMessage;
      if (!name && stateReloadNeeded) return "Не удалось загрузить данные аккаунта. Проверьте соединение и повторите загрузку.";
      if (name === "login" && error.status === 401) return "Не удалось войти. Проверьте имя пользователя и пароль.";
      if (error.status === 401) return "Для сохранения настроек нужно войти. Обновите состояние и войдите снова.";
      if (error.code === "SESSION_CHANGED") return "Сеанс изменился. Обновите состояние и проверьте, в какой аккаунт выполнен вход.";
      if (error.status === 403) return "Не удалось подтвердить безопасность запроса. Повторите запрос для обновления проверки.";
      if (error.status === 409) return "Запрос конфликтует с сохранённым состоянием. Обновите состояние перед новой попыткой.";
      if (error.status === 429) return "Слишком много попыток входа. Подождите перед повторной попыткой.";
      if (error.status === 400) return name === "register"
        ? "Не удалось зарегистрироваться с этими данными. Проверьте имя, пароль и почту."
        : "Не удалось сохранить выбранные данные. Проверьте форму и доступный список классов.";
      return "Не удалось подтвердить результат запроса. Проверьте соединение и повторите попытку.";
    }
    function showError(error, name = null, focus = true) {
      const message = errorMessage(error, name);
      el("account-state").hidden = false;
      el("account-error").textContent = message;
      el("account-error").hidden = false;
      el("account-state").dataset.state = "error";
      if (name) {
        el(name + "-error").textContent = message;
        el(name + "-error").hidden = false;
        const mapping = {username: name + "-username", password: name + "-password",
          email: name + "-email", selected_grade_id: name + "-grade", mode: "onboarding-mode"};
        for (const [field, messages] of Object.entries(error.fieldErrors || {})) {
          const input = el(mapping[field]), target = input && el(input.id + "-error");
          if (input && target && Array.isArray(messages) && messages.every(item => typeof item === "string")) {
            target.textContent = messages.join(" ");
            target.hidden = false;
            input.setAttribute("aria-invalid", "true");
          }
        }
      }
      if (focus) el("account-error").focus();
    }
    function renderSaved(restore = false) {
      el("anonymous-panel").hidden = !sessionReady || profile !== null;
      el("profile-panel").hidden = !sessionReady || profile === null;
      if (!profile) {
        for (const name of ["saved-username", "saved-grade", "saved-mode", "saved-completion"]) el(name).textContent = "";
        if (restore) {
          for (const select of selects) select.value = "";
          for (const name of radioIds) el(name).checked = false;
        }
        return;
      }
      el("saved-username").textContent = profile.username;
      const grade = catalogue.find(item => String(item.id) === String(profile.selected_grade_id));
      el("saved-grade").textContent = grade ? grade.title : profile.selected_grade_id === null
        ? "Класс пока не выбран" : gradesReady ? "Сохранённый класс сейчас недоступен в каталоге" : "Класс сохранён; название пока не загружено";
      el("saved-mode").textContent = modeLabels[profile.onboarding_mode] || "Путь пока не выбран";
      el("saved-completion").textContent = profile.onboarding_complete ? "Настройка сохранена" : "Настройка ещё не сохранена";
      if (restore) {
        for (const select of selects) select.value = grade ? String(grade.id) : "";
        for (const name of radioIds) el(name).checked = el(name).value === profile.onboarding_mode;
      }
    }
    async function readSaved() {
      try {
        profile = await client.me();
        sessionReady = true;
        stateReloadNeeded = false;
        renderSaved(true);
      } catch (error) {
        sessionReady = false;
        stateReloadNeeded = true;
        renderSaved();
        throw error;
      } finally { controls(); }
    }
    async function loadGrades() {
      if (gradesLoading) return;
      gradesLoading = true;
      const previous = selects.map(select => select.value);
      gradesReady = false;
      controls();
      el("grades-error").hidden = true;
      el("grades-retry").hidden = true;
      el("grades-status").textContent = "Загружаем классы…";
      try {
        catalogue = await client.grades();
        gradesReady = true;
        for (const [index, select] of selects.entries()) {
          select.replaceChildren();
          const placeholder = doc.createElement("option");
          placeholder.value = ""; placeholder.textContent = "Выберите класс";
          select.append(placeholder);
          for (const grade of catalogue) {
            const option = doc.createElement("option");
            option.value = String(grade.id); option.textContent = grade.title;
            select.append(option);
          }
          const wanted = previous[index] || (profile && profile.selected_grade_id);
          select.value = catalogue.some(row => String(row.id) === String(wanted)) ? String(wanted) : "";
        }
        el("grades-status").textContent = catalogue.length ? "Список классов загружен." : "Доступных классов пока нет.";
        renderSaved();
      } catch (_) {
        el("grades-status").textContent = "Список классов не загружен.";
        el("grades-error").textContent = "Не удалось загрузить классы. Попробуйте ещё раз.";
        el("grades-error").hidden = false;
        el("grades-retry").hidden = false;
      } finally { gradesLoading = false; controls(); }
    }
    function clearCredentials() {
      el("register-password").value = "";
      el("login-password").value = "";
    }
    function matches(operation, current) {
      const body = JSON.parse(operation.body);
      if (operation.name === "logout") return current === null;
      if (operation.name === "login") return current && current.username === body.username;
      if (operation.name === "profile") return current && String(current.selected_grade_id) === String(body.selected_grade_id);
      return false;
    }
    async function acknowledged(name) {
      pending = null;
      retryAt = 0;
      clearCredentials();
      if (name === "logout") { authMode = "login"; renderAuth(); }
      // Never turn a historical mutation receipt into the current profile.
      sessionReady = false;
      renderSaved();
      if (["register", "login"].includes(name)) await client.csrf();
      await readSaved();
      announce(name === "logout" ? "Вы вышли. Настройки аккаунта сохранены." : "Сохранённое состояние обновлено.");
    }
    async function execute(retry = false) {
      if (busy || !pending || Date.now() < retryAt) return;
      busy = true;
      controls();
      clearErrors();
      announce("Отправляем запрос…", "loading");
      const attempt = pending, operation = attempt.operation;
      let accepted = false;
      try {
        if (attempt.owner !== null || (retry && !operation.key)) {
          const current = await client.me();
          if (attempt.owner !== null && current && String(current.id) !== String(attempt.owner)) {
            throw {code: "SESSION_CHANGED", status: 409};
          }
          if (retry && !operation.key && matches(operation, current)) {
            accepted = true;
            await acknowledged(operation.name);
            return;
          }
          if (attempt.owner !== null && !current) throw {status: 401};
        }
        await client.send(operation);
        accepted = true;
        await acknowledged(operation.name);
      } catch (error) {
        // After a known acknowledgement only restore state; do not resend the mutation.
        stateReloadNeeded = stateReloadNeeded || accepted || error.code === "SESSION_CHANGED"
          || error.status === 409 || (error.status === 401 && operation.name !== "login");
        pending = !accepted && (error.retryable || error.status === 403) ? attempt : null;
        retryAt = error.status === 429 ? Date.now() + (error.retryAfter || 1) * 1000 : 0;
        if (retryAt) {
          clearTimeout(retryTimer);
          retryTimer = setTimeout(controls, Math.max(0, retryAt - Date.now()));
        }
        announce(accepted ? "Запрос принят. Обновите сохранённое состояние." : "Результат пока не подтверждён.");
        showError(error, operation.name);
        if (error.status === 401 && operation.name !== "login") {
          sessionReady = false;
          renderSaved();
        }
      } finally {
        if (!pending && ["register", "login"].includes(operation.name)) clearCredentials();
        busy = false;
        controls();
        // Native inputs can receive focus only after their fieldset is enabled.
        if (accepted && sessionReady) {
          if (["register", "login"].includes(operation.name)) el("profile-title").focus();
          if (operation.name === "logout") el("login-username").focus();
        }
      }
    }
    const payloads = {
      register: () => ({username: value("register-username"), password: value("register-password"),
        ...(value("register-email") ? {email: value("register-email")} : {})}),
      login: () => ({username: value("login-username"), password: value("login-password")}),
      logout: () => ({}),
      profile: () => ({selected_grade_id: selectedID("profile-grade")}),
      onboarding: () => ({selected_grade_id: selectedID("onboarding-grade"),
        mode: radioIds.map(el).find(input => input.checked).value})
    };
    for (const name of formNames) {
      forms[name].addEventListener("submit", async event => {
        event.preventDefault();
        if (busy || pending || !sessionReady || (["login", "register"].includes(name) && name !== authMode)) return;
        // Native maxlength also limits typing/paste; guard prefilled/programmatic values before creating an action/key.
        if (name === "register" && value("register-username").length > 30) {
          clearCredentials();
          clearErrors();
          showError({status: 400, code: "USERNAME_TOO_LONG", fieldErrors: {username: [usernameLimitMessage]}}, name);
          return;
        }
        if (!forms[name].reportValidity()) return;
        try {
          pending = {operation: client.action(name, payloads[name]()), owner: profile ? profile.id : null};
          // Retry uses the serialized operation, never credentials retained in form inputs.
          if (["register", "login"].includes(name)) clearCredentials();
          await execute();
        } catch (_) {
          pending = null;
          if (["register", "login"].includes(name)) clearCredentials();
          showError({status: 400}, name); controls();
        }
      });
    }
    for (const name of ["login", "register"]) {
      el("auth-" + name).addEventListener("click", () => {
        if (busy || pending || !sessionReady || profile) return;
        if (name !== authMode) el(authMode + "-password").value = "";
        authMode = name;
        clearErrors();
        renderAuth();
        controls();
        el(name + "-username").focus();
      });
    }
    el("account-retry").addEventListener("click", () => execute(true));
    el("account-refresh").addEventListener("click", async () => {
      if (busy) return;
      busy = true; controls(); clearErrors();
      announce("Загружаем сохранённое состояние…", "loading");
      try { await readSaved(); announce("Сохранённое состояние загружено."); }
      catch (error) {
        announce("Не удалось загрузить сохранённое состояние.", "error");
        showError(error);
      }
      finally {
        busy = false; controls();
        // Successful recovery hides its button: move focus to a usable control.
        if (!stateReloadNeeded) {
          if (pending) el("account-retry").focus();
          else el(profile ? "profile-title" : authMode + "-username").focus();
        }
      }
    });
    el("grades-retry").addEventListener("click", () => {
      if (!busy && !pending) return loadGrades();
    });
    async function start() {
      busy = true; controls();
      try { await client.csrf(); await readSaved(); announce(profile ? "Сохранённое состояние загружено." : ""); }
      catch (error) {
        stateReloadNeeded = true;
        announce("Не удалось загрузить сохранённое состояние.", "error");
        showError(error, null, false);
      }
      finally { busy = false; controls(); }
    }
    renderAuth();
    const ready = Promise.all([start(), loadGrades()]);
    return {ready};
  }
  return {mount};
});
