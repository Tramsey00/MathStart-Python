import { useEffect, useState } from 'react';
import { parseJson } from '../../shared/api/json-boundary';
import { isPublicExercise, type PublicExercise } from '../../shared/exercise/dispatcher';
import { Button } from '../../shared/ui/components';
import { IdentityIcon } from '../identity/identity-icon';
import { safeReturn, useSession } from '../identity/session';
import { exerciseForm } from './exercise-contract';
import { PracticeEditor } from './practice-editor';

export const practiceSection = { id: 'practice', title: 'Практика' };
const pilots = new Set([
  'polozhitelnye-i-otriczatelnye-chisla-opredelenie-koordinatnoj-pryamoj',
  'algebraicheskaya-summa-raczionalnyh-chisel-s-raznymi-znakami',
  'umnozhenie-i-delenie-raczionalnyh-chisel',
  'uproshhenie-vyrazhenij-raskrytie-skobok',
  'reshenie-linejnyh-uravnenij',
]);
const anchorPattern = /^#practice-exercise-([\da-f]{8}(?:-[\da-f]{4}){3}-[\da-f]{12})$/i;

export function isPracticeTopic(slug: string) {
  return pilots.has(slug);
}

function exerciseAnchor(id: string) {
  return 'practice-exercise-' + id;
}

function selectedFromLocation() {
  return window.location.hash.match(anchorPattern)?.[1]?.toLowerCase() ?? null;
}

function loginHref(path: string, selected: string | null) {
  const target = safeReturn(path + '#' + (selected ? exerciseAnchor(selected) : practiceSection.id));
  return '/auth?' + new URLSearchParams({ mode: 'login', return: target });
}

export function LessonPractice({ slug, path }: { slug: string; path: string }) {
  const { user, status, refresh } = useSession();
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    const readHash = () => setSelected(selectedFromLocation());
    readHash();
    window.addEventListener('hashchange', readHash);
    return () => window.removeEventListener('hashchange', readHash);
  }, []);

  function choose(id: string | null) {
    history.replaceState(history.state, '', '#' + (id ? exerciseAnchor(id) : practiceSection.id));
    setSelected(id);
  }

  return <section className="lesson-section practice-section" id={practiceSection.id} tabIndex={-1} aria-labelledby="practice-title">
    <h2 id="practice-title">{practiceSection.title}</h2>
    {status === 'checking' && <p role="status">Проверяем вход…</p>}
    {status === 'error' && <div className="practice-recovery">
      <p role="status">Не удалось проверить вход.</p>
      <Button onClick={() => void refresh()}>Попробовать снова</Button>
    </div>}
    {status === 'ready' && !user && <div className="practice-gate worked-example">
      <div className="practice-gate-preview" aria-hidden="true" inert>
        <span/><span/><span/><span/>
      </div>
      <div className="practice-gate-copy">
        <IdentityIcon name="lock"/>
        <p>Задания с помощником доступны только авторизованным пользователям</p>
        <a className="practice-primary" href={loginHref(path, selected)}>Войти</a>
      </div>
    </div>}
    {status === 'ready' && user && <ExerciseList key={String(user.id)} owner={String(user.id)} slug={slug}
      selected={selected} choose={choose} onSessionChange={() => void refresh()} login={loginHref(path, selected)}/>}
  </section>;
}

type LoadState =
  | { state: 'loading' | 'error' | 'unsupported' | 'unauthorized' }
  | { state: 'ready'; exercises: PublicExercise[] };

async function readBank(slug: string, signal: AbortSignal): Promise<LoadState> {
  const exercises: PublicExercise[] = [];
  const seen = new Set<string>();
  let cursor: string | null = null;
  try {
    do {
      const params = new URLSearchParams({ page_size: '20' });
      if (cursor) params.set('cursor', cursor);
      const response = await fetch('/api/v1/topics/' + encodeURIComponent(slug) + '/exercises/?' + params, {
        credentials: 'same-origin', cache: 'no-store', redirect: 'error',
        headers: { Accept: 'application/json' }, signal: AbortSignal.any([signal, AbortSignal.timeout(12_000)]),
      });
      if (response.status === 401) return { state: 'unauthorized' };
      if (!response.ok || !/^application\/json(?:\s*;.*)?$/i.test(response.headers.get('Content-Type') ?? '')) return { state: 'error' };
      const bytes = await response.arrayBuffer();
      if (bytes.byteLength > 1_048_576) return { state: 'error' };
      const payload = parseJson(new TextDecoder('utf-8', { fatal: true }).decode(bytes)) as {
        data?: unknown; meta?: { version?: unknown; pagination?: { next_cursor?: unknown } };
      } | null;
      if (payload?.meta?.version !== 'http-v1' || !Array.isArray(payload.data)) return { state: 'error' };
      for (const exercise of payload.data) {
        if (!isPublicExercise(exercise) || exercise.topic.slug !== slug || exercise.exercise_version.status !== 'PUBLISHED') {
          return { state: 'unsupported' };
        }
        if (exercise.interaction_mode === 'FINAL_ANSWER' || exercise.interaction_mode === 'STEP_BY_STEP') exercises.push(exercise);
      }
      const next = payload.meta.pagination?.next_cursor;
      if (next !== null && (typeof next !== 'string' || next.length < 1 || next.length > 1024 || seen.has(next))) return { state: 'error' };
      cursor = next;
      if (cursor) seen.add(cursor);
    } while (cursor);
    return { state: 'ready', exercises };
  } catch {
    return { state: 'error' };
  }
}

function ExerciseList({ owner, slug, selected, choose, login, onSessionChange }: {
  owner: string; slug: string; selected: string | null; choose: (id: string | null) => void;
  login: string; onSessionChange: () => void;
}) {
  const [result, setResult] = useState<LoadState>({ state: 'loading' });
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    void readBank(slug, controller.signal).then(value => {
      if (!controller.signal.aborted) setResult(value);
    });
    return () => controller.abort();
  }, [slug, retry]);

  useEffect(() => {
    if (result.state !== 'ready') return;
    const target = selectedFromLocation();
    if (!target) return;
    const card = document.getElementById(exerciseAnchor(target)) ?? document.getElementById(practiceSection.id);
    card?.focus({ preventScroll: true });
    card?.scrollIntoView({ block: 'start' });
  }, [result]);

  if (result.state === 'loading') return <p role="status">Загружаем задания…</p>;
  if (result.state === 'unauthorized') return <div className="practice-recovery">
    <p role="status">Войдите, чтобы открыть практику.</p><a className="practice-primary" href={login}>Войти</a>
  </div>;
  if (result.state === 'unsupported') return <p role="status">Эта версия заданий пока недоступна на странице урока.</p>;
  if (result.state !== 'ready') return <div className="practice-recovery">
    <p role="status">Не удалось загрузить задания.</p>
    <Button onClick={() => { setResult({ state: 'loading' }); setRetry(value => value + 1); }}>Попробовать снова</Button>
  </div>;
  if (!result.exercises.length) return <p>В этом уроке пока нет заданий для отправки.</p>;

  return <div className="practice-exercises">
    {selected && !result.exercises.some(exercise => exercise.id === selected) && <p role="status">Выбранное задание больше недоступно.</p>}
    {result.exercises.map(exercise => {
      const form = exerciseForm(exercise);
      const id = exerciseAnchor(exercise.id);
      const open = selected === exercise.id;
      return <article className="worked-example practice-exercise" id={id} key={exercise.exercise_version.id}
        aria-labelledby={id + '-statement'} tabIndex={-1}>
        <h3 id={id + '-statement'}>{exercise.statement}</h3>
        {!form ? <p>Такая форма решения пока недоступна.</p> : <>
          <Button className="practice-toggle" aria-expanded={open} aria-controls={id + '-editor'} onClick={() => choose(open ? null : exercise.id)}>
            {open ? 'Свернуть' : form.mode === 'final-answer' ? 'Ввести ответ' : 'Записать шаги'}
          </Button>
          <div id={id + '-editor'} hidden={!open}>
            {open && <PracticeEditor form={form} exercise={exercise} owner={owner} login={login} onSessionChange={onSessionChange}/>}
          </div>
        </>}
      </article>;
    })}
  </div>;
}
