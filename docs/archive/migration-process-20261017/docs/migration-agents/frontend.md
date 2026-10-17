# Профиль frontend-агента миграции

Это профиль делегируемой роли. Начинать только после задания координатора.
Прочитать [AGENT](../../MIGRATION_AGENT.md), [TASKS](../../MIGRATION_TASKS.md),
[VERIFICATION](../../MIGRATION_VERIFICATION.md), [STATE](../../MIGRATION_STATE.md).

## Назначение и владение

I02–I06 и обязательные I01 follow-ups. I02 реализовать с нуля от accepted I01/V02/R02;
не ждать и не импортировать прежние неопубликованные consumer наработки.
Получить отдельный checkout, exact SHA, writable paths, ports/runtime roots.
Один writer владеет frontend lock/routes; backend/CI/root registry передавать
координатору или backend-роли через точный interface/patch.

## Неизменяемая основа

React/TypeScript, принятые Vite/React Router и locks, существующий дизайн/CSS.
Без глобального reset, новой UI-библиотеки, массового JSX conversion уроков
и permanent Node SSR server. Не добавлять будущие упражнения/прогресс/AI.
Читать UX states, frozen wire contracts и реальные V02 rendering interfaces.

## Последовательность

1. I02: shell/pages/catalogue/staff read UI + SSG всех public URLs. Получить
   проверенные immutable V04 index/pages/assets, а не требовать active release.
   Проверить raw body/head/no-JS/SEO, search/aliases/404/redirects/sitemap/robots,
   exact IDs и release pinning. Source mock не считать real API evidence.
2. I03: LessonHost reviewed HTML/math/SVG/CSS, полные local/shared script families,
   mount/dispose либо full navigation, StrictMode/back-forward/resize/cleanup,
   F01–F04. Существующие self-check остаются unassessed.
3. I04 после real V03: account/onboarding/staff forms, прежние UX/limits,
   password cleanup, frozen retry, CSRF refresh, GET-first reconciliation,
   cancellation/stale isolation и server authorization.
4. I05 с V05: Chrome/Edge/Firefox, 360/768/1440, keyboard/focus, visual parity,
   real API/security/error/recovery flows; закрыть fixture overlap и query P3.
5. I06 после V06 handoff: clean locked build/SSG/E2E, matching backend/release,
   immutable manifest/hashes, final smoke и previous compatible artifact.

## Доверие и проверка

Public DTO не содержит answer keys/checkers; user/LLM strings escaped, HTML
только из trusted publication. Account/staff PII/credentials не попадают в
SSG/debug fixtures/bundles/cache. Credentials не хранить в browser storage.
Lossless int64 transport проверить без округления и изменения frozen schemas.
Frontend role/button не является авторизацией. Unknown mutation result не
превращать в success и не повторять unsafe запрос автоматически.

Сохранить все 263 topic sources и весь manifest ресурсов; representative
captures дополняют, но не заменяют полное inventory. Новый `test:e2e` должен
существовать и завершаться с корректным cleanup. Указать реальные browser
versions; недоступный браузер оставляет соответствующую проверку pending.

## Передача

Task/slice + base/head/tree, package/lock versions, exact build input/output
digests, API/release identity, команды, screenshots/DOM/network/console без
секретов, test IDs/exit/counts и cleanup. Отдельный reviewer получает source
diff и фактические outputs; после fixes обновить evidence на новом SHA.
Не выполнять integration push самостоятельно и не выдавать source compatibility
review или успешную сборку за полную browser acceptance.
