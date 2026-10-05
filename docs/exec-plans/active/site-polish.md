# EXEC PLAN: Bounded public-site polish

- Status: Active; human gate pending
- Date: 2026-10-04
- Spec: `specs/ui/site-polish.md`
- Trace: `docs/agent-traces/site-polish.md`

## Baseline and authorization

Branch `fix/topics-catalog`, HEAD `9ef93f90767b6639a0ebf3c23aa7bc9d288456d3`.
Tracked/staged tree initially clean. Preserve existing MS7-AUDIT/G0Candidate/
PREG0 untracked plans/traces, `output/`, `tmp/`. Prior task documents are context;
their status and other work remain unchanged. User's attached implementation
request authorizes only the listed local DB publication and visual edits.

Working site: local PostgreSQL `mathstart` on 127.0.0.1, DEBUG=False, port 8000.
Catalogue/About/Contacts differ from source; retired pages still published.
Source home matches DB. Restorable initial fixture/fingerprints and browser
baseline live under ignored `var/site-polish/`. Account profile table is absent
in this existing DB; do not apply account migrations within this task.

## Steps

1. Record baseline; create compact scoped page/shell markup and styles.
2. Add narrowly scoped publication using existing bootstrap/publishing services,
   conflict checks, backup and atomic update; verify isolated upgrade/repeat.
3. Apply permitted records locally, collect static, reload the intended server.
4. Run required verification/fresh smoke/browser comparisons, inspect diff,
   record evidence and leave the result for human acceptance.

## Checklist

- [x] Implementation and focused tests
- [x] Isolated upgrade and fresh/repeated bootstrap
- [x] Scoped working DB publication and live port-8000 proof
- [x] Responsive browser review, preservation checks, required verification
- [x] Final diff/trace and review artifacts
- [ ] Human acceptance (owner; never inferred)

## Scoped local update and recovery

Run from the configured `.venv312` environment:

```powershell
python manage.py update_public_pages --dry-run
python manage.py update_public_pages
python manage.py collectstatic --noinput
```

`--dry-run` validates sources/lesson conflicts and rolls back selected SQL writes;
it is not a read-only audit. Real update backs up affected public records under
`var/backups/`, retains the locked publication conflict recheck and updates DB
records in one transaction. Only the powers PDF may be copied if absent. The
existing whole-site bootstrap remains the fresh-install entry point.

Local application completed with snapshot
`var/backups/before-public-pages-20261004T192025339076Z-4f57b259.json`.
The additional before-fixture/fingerprints in `var/site-polish/` record exact
initial IDs/absence. For an intentional rollback of this application, restore
that Django fixture with `loaddata` inside a transaction and remove only the
two newly created root Redirect rows (IDs 283/284, paths `/materialy/` and
`/pamyatki/`, absent from the snapshot). Retain every other record. This rollback
has not been executed; recheck for intervening edits before an owner requests it.

## Remaining local runtime limitation

Port 8000 still runs with DEBUG=False. Its unchanged URL configuration does not
serve `/media/`; PDF HTTP returns 404 although the exact file, original URL,
published lesson link and MediaAsset relationship are preserved. Deployment
configuration changes are expressly out of scope. This is separate from the
passing manifest/CSS checks and is not presented as a passing PDF HTTP check.

## Final verification

`verify_repo.py` exited 0, PASS 8/8: 90 Django tests, 18 R03 tests, 73 Harness
tests. Five new targeted tests also pass on explicit SQLite compatibility.
Fresh PostgreSQL smoke and isolated actual-content upgrade/dry-run/repeat pass.
Live/browser evidence is in the trace and ignored artifacts. Final diff check
passes; 10 modified tracked files and 6 new task files reviewed. No schema,
configuration, curriculum-source or other-task document edits. HEAD unchanged;
staged diff empty. Keep this plan active for human acceptance.
