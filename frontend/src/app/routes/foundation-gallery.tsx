import { useRef, useState } from "react";
import type { LinksFunction, MetaFunction } from "react-router";
import { Button, Card, Field, State, type ViewState } from "../../shared/ui/components";
import { dispatchExercise } from "../../shared/exercise/dispatcher";
import { fixtures } from "../../debug/fixture-pack";
import tokens from "../../../../static/mathstart/css/ui/tokens.css?url";
import foundation from "../../../../static/mathstart/css/ui/foundation.css?url";
export const links:LinksFunction=()=>[{rel:"stylesheet",href:tokens},{rel:"stylesheet",href:foundation}];
export const meta:MetaFunction=()=>[{title:"UI foundation · MathStart · Fixture only"},{name:"robots",content:"noindex, nofollow"}];
export const handle={skipLink:{target:"foundation-main",label:"К примерам интерфейса"}};
const fieldError="Пример ошибки поля. Текст не проверялся и не был сохранён.";
export default function FoundationGallery() {
  const [state,setState]=useState<ViewState>("ordinary");
  const [changed,setChanged]=useState(false);
  const [errorVisible,setErrorVisible]=useState(false);
  const [fieldAlert,setFieldAlert]=useState("");
  const [mode,setMode]=useState("0");
  const input=useRef<HTMLInputElement>(null), selector=useRef<HTMLSelectElement>(null);
  const current=fixtures.states.find(s=>s.state===state)!;
  const slot=dispatchExercise(mode==="unsupported"?{interaction_mode:"UNKNOWN"}:fixtures.exercises[Number(mode)]);
  function showState(next:ViewState) {setState(next);setChanged(true);setFieldAlert(next==="error"?fixtures.states.find(s=>s.state===next)!.message:"");}
  return <main id="foundation-main" className="ms-ui" tabIndex={-1}>
    <p className="ms-ui-fixture-mark"><strong>FIXTURE ONLY · Только синтетические примеры</strong><br/>Не сохраняются, не оцениваются и не меняют прогресс.</p>
    <header className="ms-ui-intro">
      <p className="ms-ui-muted">MS7-I02 · UI fixtures v{fixtures.fixture_version} · {fixtures.provenance.http_artifact}</p>
      <h1>Основа интерфейса</h1>
      <p>Общие компоненты, состояния и выбор слота по публичной schema. Полные формы появятся в следующих задачах.</p>
    </header>
    <section aria-labelledby="states-title"><h2 id="states-title">Четыре состояния</h2><div className="ms-ui-grid">
      {fixtures.states.map(s=><State key={s.state} state={s.state} title={s.title}>{s.message}</State>)}
    </div></section>
    <section className="ms-ui-card" aria-labelledby="demo-title">
      <h2 id="demo-title">Проверка состояний и клавиатуры</h2>
      <p>Это локальная демонстрация: кнопки не отправляют запросы. Текст остаётся только в текущем поле.</p>
      <Field id="demo-input" label="Демонстрационный ввод" required inputRef={input} errorVisible={errorVisible}
        help="Введите любой текст. При смене состояния он останется без изменений." error={fieldError}/>
      <div className="ms-ui-field"><label htmlFor="demo-state">Демонстрационное состояние</label>
        <select ref={selector} id="demo-state" aria-controls="demo-region" value={state}
          onChange={e=>{const s=fixtures.states.find(s=>s.state===e.target.value);if(s)showState(s.state);}}>
          {fixtures.states.map(s=><option key={s.state} value={s.state}>{s.title}</option>)}
        </select>
      </div>
      <div id="demo-region" className="ms-ui-state" data-state={state} aria-busy={state==="loading"}>
        <h3 id="demo-title-current">{current.title}</h3><p id="demo-message">{current.message}</p>
        <div id="demo-retry-wrap" hidden={state!=="error"}>
          <Button id="demo-retry" aria-controls="demo-region" onClick={()=>{selector.current?.focus();showState("ordinary");}}>Повторить демонстрацию</Button>
        </div>
      </div>
      <p id="demo-status" className="ms-ui-sr-only" role="status" aria-live="polite" aria-atomic="true">{changed&&state!=="error"?current.message:""}</p>
      <p id="demo-alert" className="ms-ui-sr-only" role="alert" aria-atomic="true">{fieldAlert}</p>
      <Button id="demo-field-error" aria-controls="demo-input" onClick={()=>{
        setErrorVisible(!errorVisible);setFieldAlert(errorVisible?"":fieldError);input.current?.focus();
      }}>{errorVisible?"Убрать ошибку поля":"Показать ошибку поля"}</Button>
      <noscript><p>Динамический пример требует JavaScript. Все статические состояния доступны выше.</p></noscript>
    </section>
    <section aria-labelledby="dispatch-title"><h2 id="dispatch-title">Foundation dispatch</h2>
      <p>Распознаётся режим и форма metadata. Renderer, отправка решения и математическая проверка здесь отсутствуют.</p>
      <label htmlFor="demo-mode">Публичный режим</label>
      <select id="demo-mode" aria-controls="dispatch-result" value={mode} onChange={e=>setMode(e.target.value)}>
        {fixtures.exercises.map((e,i)=><option key={e.id} value={String(i)}>{e.interaction_mode}</option>)}
        <option value="unsupported">Неизвестный режим (негативный пример)</option>
      </select>
      <p id="dispatch-result" role="status" aria-live="polite" aria-atomic="true" data-slot={slot}>
        {slot==="unsupported"?"Этот режим или форма schema не поддерживается. Форма не создаётся; математической оценки нет.":
          "Foundation slot: "+slot+". Это только выбор слота, без формы и оценки."}
      </p>
      <div className="ms-ui-grid">{fixtures.exercises.map(e=><Card key={e.id} title={e.interaction_mode}>{e.statement}</Card>)}</div>
    </section>
  </main>;
}
