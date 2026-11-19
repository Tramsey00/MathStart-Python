import { useEffect, useEffectEvent, useRef, useState } from 'react';
import { createAttemptClient, attemptPollDelaysMs, type Attempt, type AttemptResult } from '../../shared/api/attempt-client';
import { DraftUpdateRequest } from '../../shared/api/generated/attempt-validators.mjs';
import type { PublicExercise } from '../../shared/exercise/dispatcher';
import { api } from '../identity/session';
import { emptyDraft, sameDraft, type Draft } from './exercise-contract';

const attempts = createAttemptClient();
const uuid = /^[\da-f]{8}(?:-[\da-f]{4}){3}-[\da-f]{12}$/i;

type Recovery = {
  id: string | null;
  revision: number;
  draft: Draft;
  dirty: boolean;
  saving: { revision: number; draft: Draft } | null;
  submitting: { revision: number; key: string } | null;
};

const initial: Recovery = { id: null, revision: 0, draft: emptyDraft, dirty: false, saving: null, submitting: null };

function restore(key: string, contract: number): Recovery {
  try {
    const value = JSON.parse(sessionStorage.getItem(key) ?? 'null') as Recovery | null;
    const validDraft = (draft: Draft) => DraftUpdateRequest({ expected_revision: 1, contract_version: contract, draft });
    if (value && (value.id === null || uuid.test(value.id)) && Number.isSafeInteger(value.revision)
      && value.revision >= 0 && typeof value.dirty === 'boolean' && validDraft(value.draft)
      && (value.saving === null || Boolean(value.id && value.saving.revision === value.revision && validDraft(value.saving.draft)))
      && (value.submitting === null || Boolean(value.id && value.submitting.revision === value.revision && uuid.test(value.submitting.key)))) {
      return value;
    }
  } catch {
    // Storage is optional. The server can still restore the last confirmed draft.
  }
  return initial;
}

function retryDelay(ms: number, signal: AbortSignal) {
  return new Promise<void>(resolve => {
    const finish = () => {
      clearTimeout(timer);
      signal.removeEventListener('abort', finish);
      resolve();
    };
    const timer = setTimeout(finish, ms);
    signal.addEventListener('abort', finish, { once: true });
  });
}

function submitted(attempt: Attempt) {
  return (attempt.state === 'SUBMITTED' || attempt.state === 'COMPLETED')
    && Boolean(attempt.submitted_at && attempt.operation_id && attempt.snapshot_digest);
}

type Failure = Extract<AttemptResult<unknown>, { ok: false }>;

export function useExerciseAttempt(exercise: PublicExercise, owner: string, onSessionChange: () => void) {
  const contract = exercise.contract_version;
  const version = exercise.exercise_version.id;
  const key = ['mathstart.practice.v1', owner, version].join(':');
  const [work, setWork] = useState(() => restore(key, contract));
  const current = useRef(work);
  const [remote, setRemote] = useState<Attempt | null>(null);
  const [conflict, setConflict] = useState(false);
  const [loading, setLoading] = useState(true);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState<'save' | 'submit' | null>(null);
  const [dirtyEdit, setDirtyEdit] = useState(0);
  const [storageFailed, setStorageFailed] = useState(false);
  const [message, setMessage] = useState('');
  const [locked, setLocked] = useState(false);
  const lifetime = useRef<AbortController | null>(null);
  const action = useRef(false);
  const lastSaveEdit = useRef(0);

  function persist(next: Recovery) {
    current.current = next;
    setWork(next);
    try {
      if (!next.dirty && !next.saving && !next.submitting && !next.id) sessionStorage.removeItem(key);
      else sessionStorage.setItem(key, JSON.stringify({ ...next, draft: next.dirty || next.submitting ? next.draft : emptyDraft }));
      setStorageFailed(false);
    } catch {
      setStorageFailed(true);
    }
  }

  function authChanged() {
    setLocked(true);
    onSessionChange();
  }

  function report(error: Failure, context: 'load' | 'save' | 'submit') {
    if (error.status === 401 || error.status === 403) authChanged();
    if (error.retryAfterSeconds) {
      setMessage('Повторите через ' + error.retryAfterSeconds + ' с.');
    } else if (error.code === 'LIMIT_EXCEEDED') {
      setMessage('Решение слишком длинное. Сократите запись перед отправкой.');
    } else if (error.code === 'VERSION_CONFLICT') {
      setMessage('Версия задания изменилась. Ваша запись осталась в черновике.');
    } else if (error.code === 'IDEMPOTENCY_CONFLICT') {
      setMessage('Не удалось подтвердить повтор операции. Ваша запись сохранена в редакторе.');
    } else if (error.outcome === 'unknown' && context === 'submit') {
      setMessage('Подтверждение отправки не получено. Проверьте состояние или повторите отправку.');
    } else if (error.status === 400) {
      setMessage('Сервер не принял запись. Проверьте, что поля заполнены и запись помещается в ограничение длины.');
    } else {
      setMessage(context === 'load' ? 'Не удалось загрузить черновик.' : 'Не удалось связаться с сервером. Ваша запись осталась в редакторе.');
    }
  }

  function matches(attempt: Attempt) {
    return attempt.exercise_version.id === version && attempt.exercise_version.exercise_id === exercise.id
      && attempt.exercise_version.contract_version === contract && attempt.interaction_mode === exercise.interaction_mode;
  }

  // A GET can confirm a lost PUT only if both the revision and exact raw draft match.
  function accept(attempt: Attempt) {
    const local = current.current;
    if (!matches(attempt) || (local.id && local.id !== attempt.id)) {
      setMessage('Сервер вернул данные другого задания.');
      return false;
    }
    setRemote(attempt);
    const same = sameDraft(local.draft, attempt.draft);
    const recovered = local.saving && attempt.revision === local.saving.revision + 1
      && sameDraft(local.saving.draft, attempt.draft);
    const original = (local.id === null && attempt.revision === 1) || local.revision === attempt.revision;
    const unsynced = local.dirty || Boolean(local.submitting);
    const collision = unsynced && !same && ((!original && !recovered) || attempt.state !== 'STARTED');
    if (collision) {
      if (!local.dirty) persist({ ...local, dirty: true });
      setConflict(true);
      return true;
    }
    setConflict(false);
    persist({
      id: attempt.id,
      revision: attempt.revision,
      draft: unsynced && !same ? local.draft : attempt.draft,
      dirty: unsynced && !same,
      saving: null,
      submitting: attempt.state === 'STARTED' && local.submitting?.revision === attempt.revision ? local.submitting : null,
    });
    return true;
  }

  async function getAttempt(id: string, signal: AbortSignal) {
    return attempts.call('get_attempt', { id, signal: requestSignal(signal) });
  }

  async function load(signal: AbortSignal) {
    setLoading(true);
    setMessage('');
    try {
      const local = current.current;
      if (local.id) {
        const result = await getAttempt(local.id, signal);
        if (signal.aborted) return;
        if (!result.ok) {
          report(result, 'load');
          return;
        }
        setReady(accept(result.value.data));
        return;
      }

      // N009 lists attempts for the owner in ascending order. Restore the latest
      // active or submitted attempt for this immutable exercise version.
      let latest: Attempt | undefined;
      let cursor: string | null = null;
      const seen = new Set<string>();
      do {
        const result = await attempts.call('list_attempts', {
          query: cursor ? { page_size: 10, cursor } : { page_size: 10 }, signal: requestSignal(signal),
        });
        if (signal.aborted) return;
        if (!result.ok) {
          report(result, 'load');
          return;
        }
        for (const row of result.value.data) {
          if (matches(row) && (row.state === 'STARTED' || submitted(row))) latest = row;
        }
        cursor = result.value.meta.pagination?.next_cursor ?? null;
        if (cursor && seen.has(cursor)) {
          setMessage('Не удалось загрузить черновик.');
          return;
        }
        if (cursor) seen.add(cursor);
      } while (cursor);
      setReady(!latest || accept(latest));
    } finally {
      if (!signal.aborted) setLoading(false);
    }
  }

  const initialLoad = useEffectEvent(load);
  useEffect(() => {
    const controller = new AbortController();
    lifetime.current = controller;
    void initialLoad(controller.signal);
    return () => controller.abort();
  }, []);

  function edit(draft: Draft) {
    persist({ ...current.current, draft, dirty: true });
    setMessage('');
    setDirtyEdit(value => value + 1);
  }

  async function save(signal: AbortSignal) {
    let local = current.current;
    if (local.saving && local.id) {
      const result = await getAttempt(local.id, signal);
      if (signal.aborted) return false;
      if (!result.ok) {
        report(result, 'save');
        return false;
      }
      if (!accept(result.value.data) || current.current.saving || result.value.data.state !== 'STARTED') return false;
      local = current.current;
    }
    if (!local.id) {
      const result = await attempts.call('create_attempt', {
        body: { exercise_id: exercise.id, version: exercise.version, contract_version: contract },
        // Owner-scoped on the server. Both tabs (or a restart) replay the same first create.
        idempotencyKey: 'n014-first:' + version, signal: requestSignal(signal),
      });
      if (signal.aborted) return false;
      if (!result.ok) {
        report(result, 'save');
        return false;
      }
      // A replayed create response is the old revision-1 snapshot. PUT below still
      // uses that revision, so a newer draft wins and is offered for reconciliation.
      if (!accept(result.value.data)) return false;
      local = current.current;
    }
    if (!local.id || !local.dirty) return Boolean(local.id);
    const sent = { revision: local.revision, draft: local.draft };
    persist({ ...local, saving: sent });
    const result = await attempts.call('update_draft', {
      id: local.id, body: { contract_version: contract, expected_revision: sent.revision, draft: sent.draft },
      signal: requestSignal(signal),
    });
    if (signal.aborted) return false;
    if (result.ok) return accept(result.value.data) && !current.current.saving;
    if (result.outcome !== 'unknown') persist({ ...current.current, saving: null });
    if (result.status === 409) {
      const latest = await getAttempt(local.id, signal);
      if (signal.aborted) return false;
      if (latest.ok) {
        accept(latest.value.data);
        if (!current.current.dirty) setMessage('Черновик уже сохранён на сервере.');
        return false;
      }
      report(latest, 'load');
      return false;
    }
    report(result, 'save');
    return false;
  }

  async function run(kind: 'save' | 'submit') {
    const signal = lifetime.current?.signal;
    if (!signal || signal.aborted || action.current || !ready || loading || locked || conflict) return;
    action.current = true;
    lastSaveEdit.current = dirtyEdit;
    setBusy(kind);
    setMessage('');
    try {
      const identity = await api.call('get_me', { signal: requestSignal(signal) });
      if (signal.aborted) return;
      if (!identity.ok) {
        report({ ...identity.error }, kind);
        return;
      }
      if (String(identity.value.data.id) !== owner) {
        authChanged();
        return;
      }
      if (!current.current.submitting && !await save(signal)) return;
      if (signal.aborted) return;
      if (kind === 'save') {
        if (!current.current.dirty) setMessage('Черновик сохранён.');
        return;
      }
      const local = current.current;
      if (!local.id || local.dirty) return;
      const pending = local.submitting ?? { revision: local.revision, key: crypto.randomUUID() };
      persist({ ...local, submitting: pending });
      const result = await attempts.call('submit_attempt', {
        id: local.id, body: { contract_version: contract, expected_revision: pending.revision },
        idempotencyKey: pending.key, signal: requestSignal(signal),
      });
      if (signal.aborted) return;
      if (result.ok && matches(result.value.data) && result.value.data.id === local.id
          && submitted(result.value.data) && sameDraft(local.draft, result.value.data.draft)) {
        accept(result.value.data);
        return;
      }
      if (!result.ok && result.outcome !== 'unknown' && result.status !== null
          && ![401, 403, 429, 503].includes(result.status)) {
        persist({ ...current.current, submitting: null });
      }
      if (!result.ok) report(result, 'submit');
      else setMessage('Подтверждение отправки не получено. Проверьте состояние или повторите отправку.');
      if (result.ok || result.outcome === 'unknown' || result.status === 409) {
        // An acknowledgement may have been lost after commit. Read canonical
        // state before offering a manual replay. Reads never repeat the POST.
        for (const delay of attemptPollDelaysMs) {
          await retryDelay(delay, signal);
          if (signal.aborted) return;
          const latest = await getAttempt(local.id, signal);
          if (signal.aborted) return;
          if (latest.ok && matches(latest.value.data) && latest.value.data.id === local.id
              && (latest.value.data.state !== 'STARTED' || latest.value.data.revision !== local.revision)) {
            // Keep the just-submitted raw draft if a different tab sent its own.
            persist({ ...current.current, dirty: !sameDraft(local.draft, latest.value.data.draft) });
            accept(latest.value.data);
            break;
          }
          if (!latest.ok && (latest.status === 401 || latest.status === 403)) {
            report(latest, 'load');
            break;
          }
        }
      }
    } finally {
      action.current = false;
      if (!signal.aborted) setBusy(null);
    }
  }

  const autosave = useEffectEvent(() => { void run('save'); });
  useEffect(() => {
    if (dirtyEdit === lastSaveEdit.current || !work.dirty || busy || conflict || locked || !ready || work.submitting) return;
    const timer = setTimeout(autosave, 850);
    return () => clearTimeout(timer);
  }, [dirtyEdit, ready, conflict, locked, busy, work.dirty, work.submitting]);

  function overwrite() {
    if (!remote || !work.id || remote.state !== 'STARTED') return;
    persist({ ...current.current, revision: remote.revision, saving: null, submitting: null });
    setConflict(false);
    setMessage('Ваша версия открыта. Сохраните её, чтобы обновить черновик на сервере.');
    lastSaveEdit.current = 0;
    setDirtyEdit(0);
  }

  return {
    work, remote, conflict, loading, ready, busy, storageFailed, message, locked,
    sent: Boolean(remote && submitted(remote) && !conflict), edit, run, overwrite,
    reload: () => {
      const signal = lifetime.current?.signal;
      if (signal && !action.current) void load(signal);
    },
  };
}

function requestSignal(lifetime: AbortSignal) {
  return AbortSignal.any([lifetime, AbortSignal.timeout(12_000)]);
}
