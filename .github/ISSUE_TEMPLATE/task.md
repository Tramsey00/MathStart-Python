---
name: MathStart task
about: Одно последовательное задание MathStart
title: "[MS-Nxxx] "
labels: ""
assignees: ""
---

## Задача

Стабильный ID, строка docs/tasks/INDEX.md и ссылка на canonical SKILL.md.
Если Issue/ветка/PR этого задания уже существуют, продолжить их.

## Проблема и результат

Какой конкретный сценарий изменяется, что реализовано сейчас и на каком HEAD
это проверено. Product/architecture decisions не подменять предположением.

## Scope и зависимости

Затрагиваемые модули/данные/contracts, включения и исключения. Ссылки на принятые
upstream artifacts и решения. Backend/frontend порядок определяется зависимостями.
Один исполнитель, одно активное задание, без обязательных субагентов/моделей
и постоянных персональных владельцев.

## Приёмка и ошибки

Наблюдаемое ожидаемое поведение, negative/edge cases и compatibility.
Сохранить Content ownership, raw input, server-only validation, только Progress
через validated events. Перечислить stop conditions и недостающие решения.

## Проверки

- Аffected product checks по skills/verification/SKILL.md и docs/target-runtime.md.
- `python scripts/verify_repo.py` с необходимым disposable runtime;
  `--profile pure` — только portable subset.
- Schema change: reviewed Alembic + PostgreSQL fresh/upgrade/concurrency.
- Content/frontend: source/URL/math/assets/SSG/browser checks по scope.
- `python scripts/check_workflow_docs.py`, source/preservation checks при затрагивании документации/реестров.

Записать actual SHA/tree, commands/results, failures/missing/skipped и ограничения.

## Передача

Ветка от проверенного актуального main без codex/ → реализация/самопроверка →
PR → отдельное ревью → исправления/перепроверки → человеческая приёмка →
решение пользователя о merge. Не редактировать main, force push/auto-merge запрещены.
PASS не равен ACCEPTED. После передачи следующую задачу автоматически не начинать.
