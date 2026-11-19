import { useId, useState, type FormEvent } from 'react';
import type { PublicExercise } from '../../shared/exercise/dispatcher';
import { Button } from '../../shared/ui/components';
import { completeDraft, completeStep, maxSteps, maxText, stepField, stepLabels, type Draft, type ExerciseForm, type StepType } from './exercise-contract';
import { useExerciseAttempt } from './use-exercise-attempt';

export function PracticeEditor({ form, exercise, owner, login, onSessionChange }: {
  form: ExerciseForm; exercise: PublicExercise; owner: string; login: string; onSessionChange: () => void;
}) {
  const id = useId();
  const attempt = useExerciseAttempt(exercise, owner, onSessionChange);
  const { work, remote, conflict, loading, ready, busy, storageFailed, message, locked, sent } = attempt;
  const [validation, setValidation] = useState('');

  function edit(draft: Draft) {
    attempt.edit(draft);
    setValidation('');
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!work.submitting && !completeDraft(form, work.draft)) {
      setValidation(form.mode === 'final-answer' ? 'Введите ответ.' : 'Добавьте шаг и заполните все добавленные шаги.');
      const target = form.mode === 'final-answer' ? id + '-answer'
        : work.draft.steps.length ? stepInputId(id, work.draft.steps.findIndex(step => !completeStep(form.types, step)))
        : id + '-add';
      document.getElementById(target)?.focus();
      return;
    }
    setValidation('');
    void attempt.run('submit');
  }

  if (locked) return <div className="practice-recovery">
    <p role="status">Сеанс изменился. Войдите снова, чтобы продолжить работу.</p>
    <a className="practice-primary" href={login}>Войти</a>
  </div>;

  if (!ready && !work.dirty && !work.submitting) return <div className="practice-form">
    <p role="status">{loading ? 'Загружаем черновик…' : message}</p>
    {!loading && <Button onClick={attempt.reload}>Повторить загрузку</Button>}
  </div>;

  const readOnly = sent || Boolean(work.submitting) || busy === 'submit'
    || Boolean(remote && remote.state !== 'STARTED');
  const answer = work.draft.payload.answer;
  return <form className="practice-form" onSubmit={submit}>
    <p className="practice-help" id={id + '-input-help'}>Записывайте обычным текстом. Например, <code>2x</code>, <code>2*x</code>, <code>3/4</code>.</p>
    {form.mode === 'final-answer' ? <div className="practice-field">
      <label htmlFor={id + '-answer'}>Ответ</label>
      <input type="text" id={id + '-answer'} name="answer" value={typeof answer === 'string' ? answer : ''}
        autoComplete="off" autoCapitalize="off" spellCheck={false} maxLength={maxText} readOnly={readOnly}
        aria-describedby={id + '-input-help ' + id + '-validation'} onChange={event => edit({ payload: { answer: event.target.value }, steps: [] })}/>
    </div> : <StepEditor id={id} draft={work.draft} types={form.types} readOnly={readOnly} change={edit}/>}

    <p className="practice-message" role="alert" id={id + '-validation'}>{validation}</p>
    {storageFailed && <p role="status">Вкладка не может сохранить запись для восстановления. Сохраните черновик перед обновлением страницы.</p>}
    {conflict && <div className="practice-recovery">
      <p role="status">{remote?.state === 'STARTED'
        ? 'Черновик изменился на сервере. Ваша запись осталась в редакторе.'
        : 'Эта попытка уже закрыта. Ваша запись осталась в редакторе.'}</p>
      {remote && <details>
        <summary>Посмотреть запись на сервере</summary>
        <DraftPreview draft={remote.draft} form={form}/>
      </details>}
      {remote?.state === 'STARTED' && <Button onClick={attempt.overwrite}>Продолжить с моей записью</Button>}
      {remote?.state !== 'STARTED' && <p>Её можно скопировать из полей выше.</p>}
    </div>}
    <p className="practice-message" role="status">
      {sent ? 'Решение отправлено' : loading ? 'Загружаем черновик…' : busy === 'save' ? 'Сохраняем черновик…'
        : busy === 'submit' ? 'Подтверждаем отправку…' : message}
    </p>
    {!ready && !loading && <Button onClick={attempt.reload}>Повторить загрузку</Button>}
    {!sent && !conflict && ready && (!remote || remote.state === 'STARTED') && <div className="practice-actions">
      {work.submitting && busy !== 'submit' ? <>
        <Button className="practice-primary" type="submit" disabled={loading}>Повторить отправку</Button>
        <Button onClick={attempt.reload} disabled={loading}>Проверить состояние</Button>
      </> : <>
        <Button className="practice-primary" type="submit" disabled={Boolean(busy) || loading}>Отправить решение</Button>
        <Button onClick={() => void attempt.run('save')} disabled={Boolean(busy) || loading || !work.dirty}>Сохранить черновик</Button>
      </>}
    </div>}
  </form>;
}

function stepInputId(id: string, index: number) {
  return id + '-step-' + index;
}

function StepEditor({ id, draft, types, readOnly, change }: {
  id: string; draft: Draft; types: StepType[]; readOnly: boolean; change: (draft: Draft) => void;
}) {
  const [announcement, setAnnouncement] = useState('');
  const steps = draft.steps;

  function replace(next: Draft['steps']) {
    change({ payload: {}, steps: next.map((step, index) => ({ ...step, step_no: index + 1 })) });
  }

  function focus(id: string) {
    requestAnimationFrame(() => document.getElementById(id)?.focus());
  }

  function write(index: number, type: StepType, text: string) {
    replace(steps.map((step, position) => index === position
      ? { ...step, step_type: type, payload: { [stepField(type)]: text }, raw_text: text }
      : step));
  }

  function add() {
    const type = types[0];
    if (!type || steps.length >= maxSteps) return;
    replace([...steps, { step_no: steps.length + 1, step_type: type, payload: { [stepField(type)]: '' }, raw_text: '' }]);
    focus(stepInputId(id, steps.length));
    setAnnouncement('Добавлен шаг ' + (steps.length + 1) + '.');
  }

  function move(index: number, offset: number) {
    const target = index + offset;
    const step = steps[index], neighbor = steps[target];
    if (!step || !neighbor) return;
    const next = steps.slice();
    next[index] = neighbor;
    next[target] = step;
    replace(next);
    focus(stepInputId(id, target));
    setAnnouncement('Шаг ' + (index + 1) + ' перемещён на позицию ' + (target + 1) + '.');
  }

  function remove(index: number) {
    replace(steps.filter((_, position) => position !== index));
    focus(steps.length > 1 ? stepInputId(id, Math.min(index, steps.length - 2)) : id + '-add');
    setAnnouncement('Шаг ' + (index + 1) + ' удалён.');
  }

  return <div className="practice-steps">
    {steps.length > 0 && <ol className="practice-step-list">
      {steps.map((step, index) => {
        const inputId = stepInputId(id, index);
        const stepType = types.find(type => step.step_type === type);
        const payload = stepType ? step.payload[stepField(stepType)] : undefined;
        const raw = step.raw_text ?? (typeof payload === 'string' ? payload : '');
        return <li key={index}>
          <fieldset className="practice-step">
            <legend>Шаг {index + 1}</legend>
            <div className="practice-step-fields">
              <div className="practice-field">
                <label htmlFor={inputId + '-type'}>Тип шага</label>
                <select id={inputId + '-type'} value={step.step_type} disabled={readOnly} onChange={event => {
                  const changed = types.find(type => type === event.target.value);
                  if (changed) write(index, changed, raw);
                }}>
                  {types.map(type => <option value={type} key={type}>{stepLabels[type]}</option>)}
                </select>
              </div>
              <div className="practice-field">
                <label htmlFor={inputId}>Запись шага</label>
                <input type="text" id={inputId} value={raw} maxLength={maxText} readOnly={readOnly}
                  autoComplete="off" autoCapitalize="off" spellCheck={false}
                  aria-describedby={id + '-input-help ' + id + '-validation'}
                  onChange={event => { if (stepType) write(index, stepType, event.target.value); }}/>
              </div>
            </div>
            {!readOnly && <div className="practice-step-actions">
              <Button aria-label={'Переместить шаг ' + (index + 1) + ' вверх'} disabled={index === 0} onClick={() => move(index, -1)}>Вверх</Button>
              <Button aria-label={'Переместить шаг ' + (index + 1) + ' вниз'} disabled={index === steps.length - 1} onClick={() => move(index, 1)}>Вниз</Button>
              <Button aria-label={'Удалить шаг ' + (index + 1)} onClick={() => remove(index)}>Удалить</Button>
            </div>}
          </fieldset>
        </li>;
      })}
    </ol>}
    {!readOnly && <Button id={id + '-add'} disabled={steps.length >= maxSteps} onClick={add}>Добавить шаг</Button>}
    {!readOnly && steps.length >= maxSteps && <p>Достигнут предел в 40 шагов.</p>}
    <span className="practice-announcement" role="status">{announcement}</span>
  </div>;
}

function DraftPreview({ draft, form }: { draft: Draft; form: ExerciseForm }) {
  if (form.mode === 'final-answer') {
    return <p className="practice-raw">{typeof draft.payload.answer === 'string' ? draft.payload.answer : 'Ответ пока пуст.'}</p>;
  }
  return draft.steps.length ? <ol>
    {draft.steps.map(step => {
      const type = form.types.find(value => step.step_type === value);
      const value = type ? step.payload[stepField(type)] : null;
      return <li className="practice-raw" key={step.step_no}>{type && <strong>{stepLabels[type] + ' '}</strong>}
        {step.raw_text ?? (typeof value === 'string' ? value : '')}</li>;
    })}
  </ol> : <p>В черновике пока нет шагов.</p>;
}
