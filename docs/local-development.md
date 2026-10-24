# Локальный запуск MathStart

Основной checkout — корень репозитория. Порядок веток и исключение ui/ux для
первых трёх задач — в [AGENTS](../AGENTS.md). После bootstrap каждый участник
работает в отдельной ветке своей задачи от origin/main, без codex/.

## Один сервер для переносимых учебных страниц

Все перенесённые уроки обслуживает основной FastAPI gateway на одном origin.
В текущем локальном preview это http://127.0.0.1:8131; линейный урок —
http://127.0.0.1:8131/materials/7-algebra-8. Старый адрес с номером 1 перенаправляется.
Новый урок не получает отдельный порт, Vite или статический HTTP server.

После явной подготовки собственного локального экземпляра запуск из корня:

```powershell
& var/t001-qa/target-env/Scripts/python.exe scripts/lesson_server.py
```

Команда читает приватный ignored env-file var/local/lesson-preview/private-env.json,
запускает только FastAPI и не создаёт schema/content/operator. Установка из чистого
clone остаётся MS-T002A. Контент публикуется через явный prepare/build/publication.

## Исторический preview утверждённого дизайна

Для просмотра новой главной, каталога и React-эталона урока достаточно tracked
исходников и Node 24.21.0/npm 11.19.0. Из корня репозитория:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev:design
```

Главная: http://127.0.0.1:5173/; материалы: http://127.0.0.1:5173/materials.html;
эталон квадратичной функции: http://127.0.0.1:5173/materials/8-algebra-32.
Для этого preview Docker, Python, БД и var/local владельца не нужны.
Команда должна выполняться из ветки/commit, где опубликованы новые исходники.
Незакоммиченные локальные изменения автора не появляются в чужом clone.

Это временный самостоятельный preview. Команда npm run dev пока использует
основную оболочку на 5171 и требует подготовленные public inputs. MS-T001 и
MS-T002 интегрируют шаблон на новом линейном уроке и public pages. Квадратичный
React preview сохраняется; его runtime-интеграция — MS-T006. MS-T002A подтверждает единый запуск итогового main
из чистого clone у другого участника. Публичный production deploy не требуется.

## Подготовленный локальный runtime FastAPI

Docker использует canonical deploy/compose.yaml и images из согласованного
commit. Приватные настройки и README конкретного экземпляра находятся в
игнорируемом var/local/. Они не должны быть скрытым prerequisite чужого clone.
Зависимости от migration-execution, tmp, исторического checkout или Django нет.

Из корня в PowerShell:

```powershell
./scripts/local.ps1 start
./scripts/local.ps1 status
./scripts/local.ps1 logs
./scripts/local.ps1 stop
```

Stop сохраняет данные. Скрипт не удаляет volumes и не перезапускает Docker/WSL.
Существующий экземпляр доступен по http://127.0.0.1:8121/, /account/ и /admin/.
Его operator — acceptance_admin; пароль владельца хранится локально в
var/local/private/operator.env. Не копировать приватные файлы/cookies в Git
или другим участникам. Точные image revisions и storage identities описаны
в локальном README экземпляра; historical имена volumes не выбирают старый код.

## Новая независимая установка

Чистый clone не содержит private settings и подготовленной БД. Используй
[release installation](../deploy/RELEASE.md): новые собственные volumes,
отдельные roles/keys, schema preview/apply/check, initial operator, immutable
prepare/build и обычные publication plan/publish. Не подключай второго writer
и не сбрасывай существующую БД ради новой установки. До замены images сохрани
проверенный backup БД и проверь совместимость по [recovery](../deploy/RECOVERY.md).

Host tools используют Python 3.12 и root requirements.lock; frontend — свой
package-lock. Подготовленный venv не считать уже существующим: при необходимости
создать его явно по locks, без Django/DRF. Отдельный pinned [oracle](legacy-oracle.md)
готовится только для необходимого historical сравнения. Полный managed QA —
[target testing](target-runtime.md); обычный локальный запуск его не выполняет.
