# MathStart Harness Adapter Protocol v1

Status: DRAFT FOR MS6-R04
Protocol version: `adapter-protocol-v1`

## 1. Purpose

Adapter Protocol отделяет MathStart Harness Runner от конкретной coding model или provider implementation.

Runner владеет:

- жизненным циклом run;
- TaskManifest;
- RunResult;
- лимитами;
- разрешением tool execution;
- repository state;
- verification;
- итоговым статусом.

Adapter владеет только преобразованием provider-specific model interaction в нормализованные события Harness.

Adapter не получает право самостоятельно обходить Runner и изменять repository state через скрытые инструменты, если такой режим объявляется enforcement-capable.

## 2. RunStatus v1

Финальные статусы RunResult:

- `READY_FOR_REVIEW`
- `FAIL`
- `BLOCKED_CONFIGURATION`
- `NEEDS_HUMAN`
- `INTERRUPTED`
- `BUDGET_EXCEEDED`

Внешнее отображение в process exit code:

| RunStatus | Exit code |
|---|---:|
| `READY_FOR_REVIEW` | 0 |
| `FAIL` | 1 |
| `BLOCKED_CONFIGURATION` | 2 |
| `NEEDS_HUMAN` | 3 |
| `INTERRUPTED` | 4 |
| `BUDGET_EXCEEDED` | 4 |

`READY_FOR_REVIEW` означает только успешное прохождение автоматической части текущего run.

Он не означает:

- merge;
- DONE;
- human acceptance;
- прохождение G1;
- разрешение deploy/push.

## 3. Adapter identity

Каждый adapter объявляет:

- `name`;
- `version`;
- `protocol_version`.

Пример:

```json
{
  "name": "fake",
  "version": "1",
  "protocol_version": "adapter-protocol-v1"
}
```

## 4. AdapterCapabilities v1

Adapter обязан до model invocation объявить capabilities.

Нормативные capability fields:

```json
{
  "tool_calls": true,
  "tool_call_interception": true,
  "usage_reporting": true,
  "cancellation": true,
  "structured_output": true,
  "streaming": false,
  "resume": false
}
```

Значение каждого capability является фактической возможностью adapter, а не пожеланием Runner.

### 4.1. Capability meanings

`tool_calls`

Adapter способен вернуть нормализованный запрос модели на вызов инструмента.

`tool_call_interception`

Harness получает tool request до выполнения действия и может разрешить или отклонить его.

`usage_reporting`

Adapter способен вернуть фактические usage fields, доступные provider. Если provider не предоставляет значение, Runner не выдумывает его.

`cancellation`

Adapter поддерживает контролируемое прекращение активного model interaction.

`structured_output`

Adapter способен передавать нормализованные структурированные ответы, требуемые protocol.

`streaming`

Adapter поддерживает stream provider events. Streaming не является обязательным для R04.

`resume`

Adapter поддерживает provider-level продолжение ранее существовавшей сессии. Это не то же самое, что Harness `resume` run.

## 5. Enforcement capability

Adapter считается потенциально пригодным для enforcement только если:

```text
tool_calls = true
AND
tool_call_interception = true
```

Одного запуска внешнего CLI subprocess недостаточно.

Если внешний coding-agent process выполняет собственные скрытые tool calls, которые MathStart Runner не может перехватить до действия, такой adapter обязан объявить:

```json
{
  "tool_call_interception": false
}
```

Такой adapter может применяться только в явно обозначенном advisory/bootstrap режиме и не является доказательством полного Harness enforcement.

## 6. Normalized model events

Adapter возвращает Runner ровно один нормализованный event за protocol step.

Допустимые типы v1:

- `MESSAGE`
- `TOOL_REQUEST`
- `FINISHED`
- `ERROR`

Неизвестный event type является protocol error.

## 7. MESSAGE

`MESSAGE` передаёт видимый model output, который не требует tool execution.

Минимальная форма:

```json
{
  "type": "MESSAGE",
  "content": "text"
}
```

Runner сохраняет `MESSAGE.content` в protocol events evidence. MESSAGE является
промежуточным событием и сам по себе не запускает verification и не назначает PASS.

После MESSAGE Runner вызывает `continue_after_message(ModelRequest)` для следующего
protocol step. Adapter сохраняет состояние сессии; request содержит текущий run/task,
новый номер turn и последний MESSAGE в `messages` как assistant content. Следующее
событие может быть MESSAGE, TOOL_REQUEST, FINISHED или ERROR. Каждый вызов учитывается
в max_turns и общем deadline, включая MESSAGE-only loops.

R04 не использует MESSAGE как доказательство успешной verification.

Model summary не заменяет фактический результат check.

## 8. TOOL_REQUEST

Минимальная форма:

```json
{
  "type": "TOOL_REQUEST",
  "call_id": "call-001",
  "tool_name": "read_file",
  "arguments": {
    "path": "PRODUCT.md"
  }
}
```

Требования:

- `call_id` уникален внутри run;
- `tool_name` не пуст;
- `arguments` является object;
- adapter не исполняет tool самостоятельно в interception-capable режиме;
- Runner получает request до handler execution.

В R04 используется минимальный fake tool set только для проверки control loop.

Полный typed Tool Registry относится к R05.

## 9. ToolResult

После обработки `TOOL_REQUEST` Runner возвращает adapter нормализованный ToolResult.

Форма:

```json
{
  "call_id": "call-001",
  "status": "OK",
  "output": {
    "text": "..."
  }
}
```

Допустимые status v1:

- `OK`
- `DENIED`
- `ERROR`

`call_id` обязан совпадать с исходным `TOOL_REQUEST`.

В R04 `DENIED` может использоваться только для базовых contract/scope smoke cases.

Полный policy/hook deny pipeline относится к R06.

## 10. FINISHED

Форма:

```json
{
  "type": "FINISHED",
  "summary": "fixture complete"
}
```

`FINISHED` завершает model loop, но не назначает RunStatus.

После `FINISHED` Runner самостоятельно:

1. фиксирует repository state;
2. выполняет требуемые проверки;
3. формирует verification result;
4. определяет итоговый RunStatus;
5. сохраняет RunResult.

Adapter не может самостоятельно объявить `READY_FOR_REVIEW`.

## 11. ERROR

Форма:

```json
{
  "type": "ERROR",
  "code": "ADAPTER_ERROR",
  "message": "safe diagnostic message",
  "retryable": false
}
```

Adapter error не должен автоматически преобразовываться в success.

Runner сопоставляет ошибку с итоговым статусом согласно lifecycle rules.

## 12. Model request

Минимальный ModelRequest v1 содержит:

```json
{
  "protocol_version": "adapter-protocol-v1",
  "run_id": "run-id",
  "task_id": "MS6-R04",
  "turn": 1,
  "messages": []
}
```

R04 не стандартизирует финальный Context Layer.

Полный pinned context, compaction и budget accounting относятся к R05.

## 13. Tool loop

Нормативная последовательность:

```text
Runner
  |
  | ModelRequest
  v
Adapter
  |
  | TOOL_REQUEST
  v
Runner
  |
  | ToolResult
  v
Adapter
  |
  | TOOL_REQUEST / MESSAGE / FINISHED / ERROR
  v
Runner
```

Минимальный синхронный интерфейс ModelAdapter:

- `identity: AdapterIdentity`;
- `capabilities: AdapterCapabilities`;
- `start(ModelRequest) -> ModelEvent`;
- `continue_with_tool_result(ToolResult) -> ModelEvent`;
- `continue_after_message(ModelRequest) -> ModelEvent`;
- `cancel() -> None`.

Runner до `start` сравнивает identity.protocol_version с ADAPTER_PROTOCOL_VERSION.
Несовпадение даёт BLOCKED_CONFIGURATION / exit 2 без model/tool/verification вызовов.

Runner увеличивает счётчик turn перед каждым вызовом start или continuation.
`continue_after_message` продолжает текущую сессию и не является provider-level resume.

При превышении `max_turns` дальнейший model step не начинается и run завершается как:

```text
BUDGET_EXCEEDED
```

## 14. Interruption

Если выполнение прервано пользователем, wall-time limit или контролируемой cancellation:

- активное выполнение прекращается;
- run не может получить `READY_FOR_REVIEW`;
- результат сохраняется как `INTERRUPTED` либо `BUDGET_EXCEEDED` согласно причине;
- доступные диагностические данные сохраняются без заявления о PASS.

Deadline общий для run: Runner проверяет его до model invocation, сразу после
возврата start/обоих continuation methods, непосредственно перед tool handler,
после handler, перед verification и перед публикацией READY_FOR_REVIEW. Verification
процессы получают remaining timeout. Expiry даёт BUDGET_EXCEEDED / exit 4; поздний
TOOL_REQUEST не исполняется, поздний FINISHED не запускает verification.

R04 не прерывает уже начавшийся blocking adapter/tool call на уровне ОС.
После обнаруженной expiry допускается сохранение диагностического результата,
но новое model/tool/check действие не начинается.

## 15. FakeAdapter v1

R04 обязана предоставить deterministic FakeAdapter.

FakeAdapter:

- не использует сеть;
- не требует API key;
- имеет фиксированную identity;
- объявляет capabilities;
- выполняет заранее заданный сценарий;
- способен вернуть `MESSAGE` и продолжить его через `continue_after_message`;
- имеет сценарии `message` (MESSAGE -> TOOL_REQUEST -> FINISHED) и `message-loop`;
- способен вернуть `TOOL_REQUEST`;
- способен принять ToolResult;
- способен вернуть `FINISHED`;
- способен симулировать `ERROR`;
- способен симулировать interruption;
- способен исчерпать `max_turns`.

Рекомендуемые capabilities FakeAdapter v1:

```json
{
  "tool_calls": true,
  "tool_call_interception": true,
  "usage_reporting": true,
  "cancellation": true,
  "structured_output": true,
  "streaming": false,
  "resume": false
}
```

Fake usage является явно синтетическим test metadata и не выдаётся за provider billing.

## 16. Real adapters

Конкретный provider или coding-agent implementation не является частью Adapter Protocol.

Будущие adapters должны реализовывать этот же protocol без изменения Runner domain contract.

Если Codex CLI или другой внешний agent runtime не позволяет MathStart перехватывать каждый tool request до выполнения, adapter обязан объявить соответствующее отсутствие capability и не используется как доказательство enforcement.

## 17. Versioning

Breaking изменение:

- event types;
- обязательных event fields;
- semantics capabilities;
- ToolResult statuses;
- ownership tool execution;

требует новой версии protocol.

Добавление provider-specific metadata не должно менять нормативную semantics v1.

Неизвестная protocol version блокирует execute до model invocation.

Протокол остаётся DRAFT: MESSAGE continuation согласован в review-correction R04 до принятия v1.
