# MathStart Harness Adapter Protocol v1

Status: DRAFT FOR MS6-R04
Protocol version: `adapter-protocol-v1`

## 1. Purpose

Adapter Protocol РѕС‚РґРµР»СЏРµС‚ MathStart Harness Runner РѕС‚ РєРѕРЅРєСЂРµС‚РЅРѕР№ coding model РёР»Рё provider implementation.

Runner РІР»Р°РґРµРµС‚:

- Р¶РёР·РЅРµРЅРЅС‹Рј С†РёРєР»РѕРј run;
- TaskManifest;
- RunResult;
- Р»РёРјРёС‚Р°РјРё;
- СЂР°Р·СЂРµС€РµРЅРёРµРј tool execution;
- repository state;
- verification;
- РёС‚РѕРіРѕРІС‹Рј СЃС‚Р°С‚СѓСЃРѕРј.

Adapter РІР»Р°РґРµРµС‚ С‚РѕР»СЊРєРѕ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµРј provider-specific model interaction РІ РЅРѕСЂРјР°Р»РёР·РѕРІР°РЅРЅС‹Рµ СЃРѕР±С‹С‚РёСЏ Harness.

Adapter РЅРµ РїРѕР»СѓС‡Р°РµС‚ РїСЂР°РІРѕ СЃР°РјРѕСЃС‚РѕСЏС‚РµР»СЊРЅРѕ РѕР±С…РѕРґРёС‚СЊ Runner Рё РёР·РјРµРЅСЏС‚СЊ repository state С‡РµСЂРµР· СЃРєСЂС‹С‚С‹Рµ РёРЅСЃС‚СЂСѓРјРµРЅС‚С‹, РµСЃР»Рё С‚Р°РєРѕР№ СЂРµР¶РёРј РѕР±СЉСЏРІР»СЏРµС‚СЃСЏ enforcement-capable.

## 2. RunStatus v1

Р¤РёРЅР°Р»СЊРЅС‹Рµ СЃС‚Р°С‚СѓСЃС‹ RunResult:

- `READY_FOR_REVIEW`
- `FAIL`
- `BLOCKED_CONFIGURATION`
- `NEEDS_HUMAN`
- `INTERRUPTED`
- `BUDGET_EXCEEDED`

Р’РЅРµС€РЅРµРµ РѕС‚РѕР±СЂР°Р¶РµРЅРёРµ РІ process exit code:

| RunStatus | Exit code |
|---|---:|
| `READY_FOR_REVIEW` | 0 |
| `FAIL` | 1 |
| `BLOCKED_CONFIGURATION` | 2 |
| `NEEDS_HUMAN` | 3 |
| `INTERRUPTED` | 4 |
| `BUDGET_EXCEEDED` | 4 |

`READY_FOR_REVIEW` РѕР·РЅР°С‡Р°РµС‚ С‚РѕР»СЊРєРѕ СѓСЃРїРµС€РЅРѕРµ РїСЂРѕС…РѕР¶РґРµРЅРёРµ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРѕР№ С‡Р°СЃС‚Рё С‚РµРєСѓС‰РµРіРѕ run.

РћРЅ РЅРµ РѕР·РЅР°С‡Р°РµС‚:

- merge;
- DONE;
- human acceptance;
- РїСЂРѕС…РѕР¶РґРµРЅРёРµ G1;
- СЂР°Р·СЂРµС€РµРЅРёРµ deploy/push.

## 3. Adapter identity

РљР°Р¶РґС‹Р№ adapter РѕР±СЉСЏРІР»СЏРµС‚:

- `name`;
- `version`;
- `protocol_version`.

РџСЂРёРјРµСЂ:

```json
{
  "name": "fake",
  "version": "1",
  "protocol_version": "adapter-protocol-v1"
}
```

## 4. AdapterCapabilities v1

Adapter РѕР±СЏР·Р°РЅ РґРѕ model invocation РѕР±СЉСЏРІРёС‚СЊ capabilities.

РќРѕСЂРјР°С‚РёРІРЅС‹Рµ capability fields:

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

Р—РЅР°С‡РµРЅРёРµ РєР°Р¶РґРѕРіРѕ capability СЏРІР»СЏРµС‚СЃСЏ С„Р°РєС‚РёС‡РµСЃРєРѕР№ РІРѕР·РјРѕР¶РЅРѕСЃС‚СЊСЋ adapter, Р° РЅРµ РїРѕР¶РµР»Р°РЅРёРµРј Runner.

### 4.1. Capability meanings

`tool_calls`

Adapter СЃРїРѕСЃРѕР±РµРЅ РІРµСЂРЅСѓС‚СЊ РЅРѕСЂРјР°Р»РёР·РѕРІР°РЅРЅС‹Р№ Р·Р°РїСЂРѕСЃ РјРѕРґРµР»Рё РЅР° РІС‹Р·РѕРІ РёРЅСЃС‚СЂСѓРјРµРЅС‚Р°.

`tool_call_interception`

Harness РїРѕР»СѓС‡Р°РµС‚ tool request РґРѕ РІС‹РїРѕР»РЅРµРЅРёСЏ РґРµР№СЃС‚РІРёСЏ Рё РјРѕР¶РµС‚ СЂР°Р·СЂРµС€РёС‚СЊ РёР»Рё РѕС‚РєР»РѕРЅРёС‚СЊ РµРіРѕ.

`usage_reporting`

Adapter СЃРїРѕСЃРѕР±РµРЅ РІРµСЂРЅСѓС‚СЊ С„Р°РєС‚РёС‡РµСЃРєРёРµ usage fields, РґРѕСЃС‚СѓРїРЅС‹Рµ provider. Р•СЃР»Рё provider РЅРµ РїСЂРµРґРѕСЃС‚Р°РІР»СЏРµС‚ Р·РЅР°С‡РµРЅРёРµ, Runner РЅРµ РІС‹РґСѓРјС‹РІР°РµС‚ РµРіРѕ.

`cancellation`

Adapter РїРѕРґРґРµСЂР¶РёРІР°РµС‚ РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕРµ РїСЂРµРєСЂР°С‰РµРЅРёРµ Р°РєС‚РёРІРЅРѕРіРѕ model interaction.

`structured_output`

Adapter СЃРїРѕСЃРѕР±РµРЅ РїРµСЂРµРґР°РІР°С‚СЊ РЅРѕСЂРјР°Р»РёР·РѕРІР°РЅРЅС‹Рµ СЃС‚СЂСѓРєС‚СѓСЂРёСЂРѕРІР°РЅРЅС‹Рµ РѕС‚РІРµС‚С‹, С‚СЂРµР±СѓРµРјС‹Рµ protocol.

`streaming`

Adapter РїРѕРґРґРµСЂР¶РёРІР°РµС‚ stream provider events. Streaming РЅРµ СЏРІР»СЏРµС‚СЃСЏ РѕР±СЏР·Р°С‚РµР»СЊРЅС‹Рј РґР»СЏ R04.

`resume`

Adapter РїРѕРґРґРµСЂР¶РёРІР°РµС‚ provider-level РїСЂРѕРґРѕР»Р¶РµРЅРёРµ СЂР°РЅРµРµ СЃСѓС‰РµСЃС‚РІРѕРІР°РІС€РµР№ СЃРµСЃСЃРёРё. Р­С‚Рѕ РЅРµ С‚Рѕ Р¶Рµ СЃР°РјРѕРµ, С‡С‚Рѕ Harness `resume` run.

## 5. Enforcement capability

Adapter СЃС‡РёС‚Р°РµС‚СЃСЏ РїРѕС‚РµРЅС†РёР°Р»СЊРЅРѕ РїСЂРёРіРѕРґРЅС‹Рј РґР»СЏ enforcement С‚РѕР»СЊРєРѕ РµСЃР»Рё:

```text
tool_calls = true
AND
tool_call_interception = true
```

РћРґРЅРѕРіРѕ Р·Р°РїСѓСЃРєР° РІРЅРµС€РЅРµРіРѕ CLI subprocess РЅРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ.

Р•СЃР»Рё РІРЅРµС€РЅРёР№ coding-agent process РІС‹РїРѕР»РЅСЏРµС‚ СЃРѕР±СЃС‚РІРµРЅРЅС‹Рµ СЃРєСЂС‹С‚С‹Рµ tool calls, РєРѕС‚РѕСЂС‹Рµ MathStart Runner РЅРµ РјРѕР¶РµС‚ РїРµСЂРµС…РІР°С‚РёС‚СЊ РґРѕ РґРµР№СЃС‚РІРёСЏ, С‚Р°РєРѕР№ adapter РѕР±СЏР·Р°РЅ РѕР±СЉСЏРІРёС‚СЊ:

```json
{
  "tool_call_interception": false
}
```

РўР°РєРѕР№ adapter РјРѕР¶РµС‚ РїСЂРёРјРµРЅСЏС‚СЊСЃСЏ С‚РѕР»СЊРєРѕ РІ СЏРІРЅРѕ РѕР±РѕР·РЅР°С‡РµРЅРЅРѕРј advisory/bootstrap СЂРµР¶РёРјРµ Рё РЅРµ СЏРІР»СЏРµС‚СЃСЏ РґРѕРєР°Р·Р°С‚РµР»СЊСЃС‚РІРѕРј РїРѕР»РЅРѕРіРѕ Harness enforcement.

## 6. Normalized model events

Adapter РІРѕР·РІСЂР°С‰Р°РµС‚ Runner СЂРѕРІРЅРѕ РѕРґРёРЅ РЅРѕСЂРјР°Р»РёР·РѕРІР°РЅРЅС‹Р№ event Р·Р° protocol step.

Р”РѕРїСѓСЃС‚РёРјС‹Рµ С‚РёРїС‹ v1:

- `MESSAGE`
- `TOOL_REQUEST`
- `FINISHED`
- `ERROR`

РќРµРёР·РІРµСЃС‚РЅС‹Р№ event type СЏРІР»СЏРµС‚СЃСЏ protocol error.

## 7. MESSAGE

`MESSAGE` РїРµСЂРµРґР°С‘С‚ РІРёРґРёРјС‹Р№ model output, РєРѕС‚РѕСЂС‹Р№ РЅРµ С‚СЂРµР±СѓРµС‚ tool execution.

РњРёРЅРёРјР°Р»СЊРЅР°СЏ С„РѕСЂРјР°:

```json
{
  "type": "MESSAGE",
  "content": "text"
}
```

R04 РЅРµ РёСЃРїРѕР»СЊР·СѓРµС‚ MESSAGE РєР°Рє РґРѕРєР°Р·Р°С‚РµР»СЊСЃС‚РІРѕ СѓСЃРїРµС€РЅРѕР№ verification.

Model summary РЅРµ Р·Р°РјРµРЅСЏРµС‚ С„Р°РєС‚РёС‡РµСЃРєРёР№ СЂРµР·СѓР»СЊС‚Р°С‚ check.

## 8. TOOL_REQUEST

РњРёРЅРёРјР°Р»СЊРЅР°СЏ С„РѕСЂРјР°:

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

РўСЂРµР±РѕРІР°РЅРёСЏ:

- `call_id` СѓРЅРёРєР°Р»РµРЅ РІРЅСѓС‚СЂРё run;
- `tool_name` РЅРµ РїСѓСЃС‚;
- `arguments` СЏРІР»СЏРµС‚СЃСЏ object;
- adapter РЅРµ РёСЃРїРѕР»РЅСЏРµС‚ tool СЃР°РјРѕСЃС‚РѕСЏС‚РµР»СЊРЅРѕ РІ interception-capable СЂРµР¶РёРјРµ;
- Runner РїРѕР»СѓС‡Р°РµС‚ request РґРѕ handler execution.

Р’ R04 РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ РјРёРЅРёРјР°Р»СЊРЅС‹Р№ fake tool set С‚РѕР»СЊРєРѕ РґР»СЏ РїСЂРѕРІРµСЂРєРё control loop.

РџРѕР»РЅС‹Р№ typed Tool Registry РѕС‚РЅРѕСЃРёС‚СЃСЏ Рє R05.

## 9. ToolResult

РџРѕСЃР»Рµ РѕР±СЂР°Р±РѕС‚РєРё `TOOL_REQUEST` Runner РІРѕР·РІСЂР°С‰Р°РµС‚ adapter РЅРѕСЂРјР°Р»РёР·РѕРІР°РЅРЅС‹Р№ ToolResult.

Р¤РѕСЂРјР°:

```json
{
  "call_id": "call-001",
  "status": "OK",
  "output": {
    "text": "..."
  }
}
```

Р”РѕРїСѓСЃС‚РёРјС‹Рµ status v1:

- `OK`
- `DENIED`
- `ERROR`

`call_id` РѕР±СЏР·Р°РЅ СЃРѕРІРїР°РґР°С‚СЊ СЃ РёСЃС…РѕРґРЅС‹Рј `TOOL_REQUEST`.

Р’ R04 `DENIED` РјРѕР¶РµС‚ РёСЃРїРѕР»СЊР·РѕРІР°С‚СЊСЃСЏ С‚РѕР»СЊРєРѕ РґР»СЏ Р±Р°Р·РѕРІС‹С… contract/scope smoke cases.

РџРѕР»РЅС‹Р№ policy/hook deny pipeline РѕС‚РЅРѕСЃРёС‚СЃСЏ Рє R06.

## 10. FINISHED

Р¤РѕСЂРјР°:

```json
{
  "type": "FINISHED",
  "summary": "fixture complete"
}
```

`FINISHED` Р·Р°РІРµСЂС€Р°РµС‚ model loop, РЅРѕ РЅРµ РЅР°Р·РЅР°С‡Р°РµС‚ RunStatus.

РџРѕСЃР»Рµ `FINISHED` Runner СЃР°РјРѕСЃС‚РѕСЏС‚РµР»СЊРЅРѕ:

1. С„РёРєСЃРёСЂСѓРµС‚ repository state;
2. РІС‹РїРѕР»РЅСЏРµС‚ С‚СЂРµР±СѓРµРјС‹Рµ РїСЂРѕРІРµСЂРєРё;
3. С„РѕСЂРјРёСЂСѓРµС‚ verification result;
4. РѕРїСЂРµРґРµР»СЏРµС‚ РёС‚РѕРіРѕРІС‹Р№ RunStatus;
5. СЃРѕС…СЂР°РЅСЏРµС‚ RunResult.

Adapter РЅРµ РјРѕР¶РµС‚ СЃР°РјРѕСЃС‚РѕСЏС‚РµР»СЊРЅРѕ РѕР±СЉСЏРІРёС‚СЊ `READY_FOR_REVIEW`.

## 11. ERROR

Р¤РѕСЂРјР°:

```json
{
  "type": "ERROR",
  "code": "ADAPTER_ERROR",
  "message": "safe diagnostic message",
  "retryable": false
}
```

Adapter error РЅРµ РґРѕР»Р¶РµРЅ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРё РїСЂРµРѕР±СЂР°Р·РѕРІС‹РІР°С‚СЊСЃСЏ РІ success.

Runner СЃРѕРїРѕСЃС‚Р°РІР»СЏРµС‚ РѕС€РёР±РєСѓ СЃ РёС‚РѕРіРѕРІС‹Рј СЃС‚Р°С‚СѓСЃРѕРј СЃРѕРіР»Р°СЃРЅРѕ lifecycle rules.

## 12. Model request

РњРёРЅРёРјР°Р»СЊРЅС‹Р№ ModelRequest v1 СЃРѕРґРµСЂР¶РёС‚:

```json
{
  "protocol_version": "adapter-protocol-v1",
  "run_id": "run-id",
  "task_id": "MS6-R04",
  "turn": 1,
  "messages": []
}
```

R04 РЅРµ СЃС‚Р°РЅРґР°СЂС‚РёР·РёСЂСѓРµС‚ С„РёРЅР°Р»СЊРЅС‹Р№ Context Layer.

РџРѕР»РЅС‹Р№ pinned context, compaction Рё budget accounting РѕС‚РЅРѕСЃСЏС‚СЃСЏ Рє R05.

## 13. Tool loop

РќРѕСЂРјР°С‚РёРІРЅР°СЏ РїРѕСЃР»РµРґРѕРІР°С‚РµР»СЊРЅРѕСЃС‚СЊ:

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

Runner СѓРІРµР»РёС‡РёРІР°РµС‚ СЃС‡С‘С‚С‡РёРє turn СЃРѕРіР»Р°СЃРЅРѕ РѕРґРЅРѕРјСѓ РїСЂРёРЅСЏС‚РѕРјСѓ protocol step.

РџСЂРё РїСЂРµРІС‹С€РµРЅРёРё `max_turns` РґР°Р»СЊРЅРµР№С€РёР№ model step РЅРµ РЅР°С‡РёРЅР°РµС‚СЃСЏ Рё run Р·Р°РІРµСЂС€Р°РµС‚СЃСЏ РєР°Рє:

```text
BUDGET_EXCEEDED
```

## 14. Interruption

Р•СЃР»Рё РІС‹РїРѕР»РЅРµРЅРёРµ РїСЂРµСЂРІР°РЅРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»РµРј, wall-time limit РёР»Рё РєРѕРЅС‚СЂРѕР»РёСЂСѓРµРјРѕР№ cancellation:

- Р°РєС‚РёРІРЅРѕРµ РІС‹РїРѕР»РЅРµРЅРёРµ РїСЂРµРєСЂР°С‰Р°РµС‚СЃСЏ;
- run РЅРµ РјРѕР¶РµС‚ РїРѕР»СѓС‡РёС‚СЊ `READY_FOR_REVIEW`;
- СЂРµР·СѓР»СЊС‚Р°С‚ СЃРѕС…СЂР°РЅСЏРµС‚СЃСЏ РєР°Рє `INTERRUPTED` Р»РёР±Рѕ `BUDGET_EXCEEDED` СЃРѕРіР»Р°СЃРЅРѕ РїСЂРёС‡РёРЅРµ;
- РґРѕСЃС‚СѓРїРЅС‹Рµ РґРёР°РіРЅРѕСЃС‚РёС‡РµСЃРєРёРµ РґР°РЅРЅС‹Рµ СЃРѕС…СЂР°РЅСЏСЋС‚СЃСЏ Р±РµР· Р·Р°СЏРІР»РµРЅРёСЏ Рѕ PASS.

## 15. FakeAdapter v1

R04 РѕР±СЏР·Р°РЅР° РїСЂРµРґРѕСЃС‚Р°РІРёС‚СЊ deterministic FakeAdapter.

FakeAdapter:

- РЅРµ РёСЃРїРѕР»СЊР·СѓРµС‚ СЃРµС‚СЊ;
- РЅРµ С‚СЂРµР±СѓРµС‚ API key;
- РёРјРµРµС‚ С„РёРєСЃРёСЂРѕРІР°РЅРЅСѓСЋ identity;
- РѕР±СЉСЏРІР»СЏРµС‚ capabilities;
- РІС‹РїРѕР»РЅСЏРµС‚ Р·Р°СЂР°РЅРµРµ Р·Р°РґР°РЅРЅС‹Р№ СЃС†РµРЅР°СЂРёР№;
- СЃРїРѕСЃРѕР±РµРЅ РІРµСЂРЅСѓС‚СЊ `TOOL_REQUEST`;
- СЃРїРѕСЃРѕР±РµРЅ РїСЂРёРЅСЏС‚СЊ ToolResult;
- СЃРїРѕСЃРѕР±РµРЅ РІРµСЂРЅСѓС‚СЊ `FINISHED`;
- СЃРїРѕСЃРѕР±РµРЅ СЃРёРјСѓР»РёСЂРѕРІР°С‚СЊ `ERROR`;
- СЃРїРѕСЃРѕР±РµРЅ СЃРёРјСѓР»РёСЂРѕРІР°С‚СЊ interruption;
- СЃРїРѕСЃРѕР±РµРЅ РёСЃС‡РµСЂРїР°С‚СЊ `max_turns`.

Р РµРєРѕРјРµРЅРґСѓРµРјС‹Рµ capabilities FakeAdapter v1:

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

Fake usage СЏРІР»СЏРµС‚СЃСЏ СЏРІРЅРѕ СЃРёРЅС‚РµС‚РёС‡РµСЃРєРёРј test metadata Рё РЅРµ РІС‹РґР°С‘С‚СЃСЏ Р·Р° provider billing.

## 16. Real adapters

РљРѕРЅРєСЂРµС‚РЅС‹Р№ provider РёР»Рё coding-agent implementation РЅРµ СЏРІР»СЏРµС‚СЃСЏ С‡Р°СЃС‚СЊСЋ Adapter Protocol.

Р‘СѓРґСѓС‰РёРµ adapters РґРѕР»Р¶РЅС‹ СЂРµР°Р»РёР·РѕРІС‹РІР°С‚СЊ СЌС‚РѕС‚ Р¶Рµ protocol Р±РµР· РёР·РјРµРЅРµРЅРёСЏ Runner domain contract.

Р•СЃР»Рё Codex CLI РёР»Рё РґСЂСѓРіРѕР№ РІРЅРµС€РЅРёР№ agent runtime РЅРµ РїРѕР·РІРѕР»СЏРµС‚ MathStart РїРµСЂРµС…РІР°С‚С‹РІР°С‚СЊ РєР°Р¶РґС‹Р№ tool request РґРѕ РІС‹РїРѕР»РЅРµРЅРёСЏ, adapter РѕР±СЏР·Р°РЅ РѕР±СЉСЏРІРёС‚СЊ СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‰РµРµ РѕС‚СЃСѓС‚СЃС‚РІРёРµ capability Рё РЅРµ РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ РєР°Рє РґРѕРєР°Р·Р°С‚РµР»СЊСЃС‚РІРѕ enforcement.

## 17. Versioning

Breaking РёР·РјРµРЅРµРЅРёРµ:

- event types;
- РѕР±СЏР·Р°С‚РµР»СЊРЅС‹С… event fields;
- semantics capabilities;
- ToolResult statuses;
- ownership tool execution;

С‚СЂРµР±СѓРµС‚ РЅРѕРІРѕР№ РІРµСЂСЃРёРё protocol.

Р”РѕР±Р°РІР»РµРЅРёРµ provider-specific metadata РЅРµ РґРѕР»Р¶РЅРѕ РјРµРЅСЏС‚СЊ РЅРѕСЂРјР°С‚РёРІРЅСѓСЋ semantics v1.

РќРµРёР·РІРµСЃС‚РЅР°СЏ protocol version Р±Р»РѕРєРёСЂСѓРµС‚ execute РґРѕ model invocation.
