/* Fixture-only local presentation: no network, storage, student writes or scoring. */
(() => {
  "use strict";
  const data = document.getElementById("ui-fixtures");
  if (!data) return;
  const pack = JSON.parse(data.textContent);
  const stateSelect = document.getElementById("demo-state");
  const region = document.getElementById("demo-region");
  const retry = document.getElementById("demo-retry");
  const retryWrap = document.getElementById("demo-retry-wrap");
  const status = document.getElementById("demo-status");
  const alert = document.getElementById("demo-alert");
  function showState(name) {
    const state = pack.states.find(item => item.state === name);
    if (!state) return;
    // Input is never re-created, replaced, normalized or persisted.
    stateSelect.value = state.state;
    region.dataset.state = state.state;
    region.setAttribute("aria-busy", String(state.state === "loading"));
    document.getElementById("demo-title-current").textContent = state.title;
    document.getElementById("demo-message").textContent = state.message;
    retryWrap.hidden = state.state !== "error";
    alert.textContent = state.state === "error" ? state.message : "";
    status.textContent = state.state === "error" ? "" : state.message;
  }
  stateSelect.addEventListener("change", () => showState(stateSelect.value));
  retry.addEventListener("click", () => {
    stateSelect.focus(); // Do not leave keyboard focus on a control about to become hidden.
    showState("ordinary");
  });
  const input = document.getElementById("demo-input");
  const fieldError = document.getElementById("demo-input-error");
  const errorButton = document.getElementById("demo-field-error");
  errorButton.addEventListener("click", () => {
    const show = fieldError.hidden;
    fieldError.hidden = !show;
    input.setAttribute("aria-invalid", String(show));
    errorButton.textContent = show ? "Убрать ошибку поля" : "Показать ошибку поля";
    input.focus();
    alert.textContent = show ? fieldError.textContent : "";
  });
  const modeSelect = document.getElementById("demo-mode");
  const result = document.getElementById("dispatch-result");
  function showMode() {
    const descriptor = modeSelect.value === "unsupported" ? {interaction_mode: "UNKNOWN"}
      : pack.exercises[Number(modeSelect.value)];
    const slot = window.MathStartUI.dispatchExercise(descriptor);
    result.dataset.slot = slot;
    result.textContent = slot === "unsupported"
      ? "Этот режим или форма schema не поддерживается. Форма не создаётся; математической оценки нет."
      : `Foundation slot: ${slot}. Это только выбор слота, без формы и оценки.`;
  }
  modeSelect.addEventListener("change", showMode);
  showMode();
})();
