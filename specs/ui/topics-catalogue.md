# SPEC: Каталог всех тем

- Статус: Реализовано и проверено; ожидается финальная человеческая приёмка
- Дата: 2026-10-04
- Владелец/reviewer scope: владелец репозитория
- Совместимость: ADR-0001, существующая публикация Content, изоляция UI MS7-I02
- План: `docs/exec-plans/active/topics-catalogue.md`

## Контракт

`/karta-sajta/` отображается как «Все темы» в навигации, заголовке и SEO title.
Показываются только опубликованные topic ContentPages, сгруппированные Grade → Subject → Section.
Пустые группы и страницы не для обучения отсутствуют. GET form принимает `q`, `grade`
(slug класса) и `subject` (slug предмета, общий для разных классов). Неизвестные значения
filter трактуются как «все»; несовместимый subject сбрасывается в «все» при смене grade.
Варианты subject берутся из опубликованных topics выбранного grade независимо от query.
Поиск обрезает окружающие пробелы и применяет Unicode casefold substring к заголовкам в Python,
чтобы PostgreSQL/SQLite вели себя одинаково. При текущем масштабе 263 topics допустима загрузка
лёгких записей заголовков/связей; тела уроков загружаются позже. API, dependency поиска и JS не нужны.

Результаты поиска сразу отображаются с контекстом grade/subject/section.
Обычный просмотр сохраняет вложенные группы и нативные details/summary. URL сохраняет состояние
отправленной формы после refresh и browser Back при неизменённом lesson URL. Reset ведёт на чистый
URL каталога. Обязательны labels, видимый focus, перенос текста и layouts для 360/768/1440.
CSS ограничен `.ms-catalogue` и повторно использует UI tokens; существующие стили уроков/главной
и XML sitemap остаются без изменений.

## Удаление и публикация

Удалять только sources для `materialy` и `pamyatki`. Во время bootstrap явно снимать публикацию
этих двух static ContentPages, сохраняя identity/content и все остальные records.
Без sweep по отсутствующим sources и без изменения migration/schema.
Обновить redirects с обоих адресов корня и `/mathstart/` напрямую на `/karta-sajta/` и
`/bazovye-svojstva-stepenej-s-naturalnym-pokazatelem/`. Сохранить байты и URL
`/media/uploads/2026/07/pamyatka-stepeni.pdf`, добавить ссылку на него в этот урок и обновить
владение MediaAsset. Обновить тексты Contacts/About. Существующее обнаружение publication conflict
остаётся активным.

## Приёмка

Tests проверяют Unicode search, комбинации filters, пустой/неверный ввод, unpublished topics,
иерархию, links, navigation, четыре 301, upgrade/repeat/bootstrap, сохранение content/media/user
и целостность sources. Запустить verify_repo и доступные visual/browser checks; явно записать
отсутствующие свидетельства. Инициализировать можно только изолированные базы.
Изменения оставить без commit. Ожидается человеческое ревью итогового UI и процедуры обновления.
