"""Read-only checks for the current sequential queue, source mappings and local links."""
from pathlib import Path
import ast
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
RETIRED = {'MS7-R05', 'MS7-R06A', 'MS7-R06B', 'MS7-R04A', 'MS7-R07', 'MS7-R08', 'MS7-V07', 'MS7-I08'}
STATUSES = {'PLANNED', 'IN_PROGRESS', 'READY_FOR_REVIEW', 'CHANGES_REQUESTED',
            'HUMAN_ACCEPTANCE_PENDING', 'ACCEPTED', 'BLOCKED_DEPENDENCY',
            'BLOCKED_DECISION', 'REMOVED_FROM_PLAN'}


def validate_queue(data, source):
    rows = data['tasks']
    ids = [r['id'] for r in rows]
    if len(set(ids)) != len(ids) or [r['order'] for r in rows] != list(range(len(rows))):
        raise ValueError('Queue IDs/order must be unique and consecutive')
    if not rows or rows[0]['id'] != 'MS-N000':
        raise ValueError('Current task must be first')
    position = {value: i for i, value in enumerate(ids)}
    for row in rows:
        if row['status'] not in STATUSES or not row.get('acceptance'):
            raise ValueError('Missing task status/acceptance: ' + row['id'])
        if len(row['dependencies']) != len(set(row['dependencies'])):
            raise ValueError('Duplicate dependency: ' + row['id'])
        for dependency in row['dependencies']:
            if dependency not in position or position[dependency] >= position[row['id']]:
                raise ValueError('Missing, cyclic or forward dependency: ' + row['id'])
            if rows[position[dependency]]['status'] == 'REMOVED_FROM_PLAN':
                raise ValueError('Dependency on retired task: ' + row['id'])
    source_ids = {r['id'] for r in source['rows']}
    for row in source['rows']:
        status = row['workflow_disposition']
        mapped = row['workflow_tasks']
        if row['id'] in RETIRED:
            if status != 'REMOVED_FROM_PLAN' or mapped:
                raise ValueError('Harness-only task must be retired, not completed')
        elif status in {'ADAPTED', 'MERGED'}:
            if not mapped or any(value not in position for value in mapped):
                raise ValueError('Missing current equivalent: ' + row['id'])
        elif status != 'COMPLETED_BASELINE' or mapped:
            raise ValueError('Unknown source disposition: ' + row['id'])
        if not row.get('workflow_reason'):
            raise ValueError('Missing disposition reason')
        expected = [r['id'] for r in rows if row['id'] in r.get('legacy_ids', [])]
        if mapped != expected:
            raise ValueError('Bidirectional source mapping differs: ' + row['id'])
    for row in rows:
        if any(value not in source_ids for value in row.get('legacy_ids', [])):
            raise ValueError('Unknown historical task ID')
    return rows


def local_links(root, documents):
    """Validate actual links; frozen source links may resolve to explicitly retired Git blobs."""
    from scripts.check_migration_preservation import dispositions, historical_artifact
    historical = dispositions(root)
    checks = []
    for name in documents:
        text = (root / name).read_text(encoding='utf-8-sig')
        # Code samples can contain illustrative Markdown syntax.
        text = re.sub(r'(?ms)^```.*?^```[^\n]*', '', text)
        for target in re.findall(r'(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)', text):
            target = target.split(' "', 1)[0].strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            relative = unquote(target.split('#', 1)[0])
            if not relative:
                continue
            path = ((root / name).parent / relative).resolve()
            if not path.is_relative_to(root.resolve()):
                raise ValueError('Documentation link escapes checkout: ' + name)
            if not path.exists():
                key = path.relative_to(root).as_posix()
                # Old source/ADR references are history, not runtime prerequisites.
                if name.startswith(('specs/', 'docs/adr/')) and key in historical:
                    historical_artifact(key, root)
                else:
                    raise ValueError('Broken local link: ' + name + ' -> ' + target)
            checks.append('local link: ' + name + ' -> ' + target)
    return checks


def verify(root=ROOT):
    queue = json.loads((root / 'docs/tasks/registry.json').read_text(encoding='utf-8'))
    source = json.loads((root / 'specs/product/task-dispositions-v7.2.json').read_text(encoding='utf-8'))
    rows = validate_queue(queue, source)
    index = (root / 'docs/tasks/INDEX.md').read_text(encoding='utf-8')
    checks = ['queue unique/order/dependencies/no cycles', 'all52 source dispositions and bidirectional mapping']
    for row in rows:
        if f"| {row['order']:02} | {row['id']} — {row['title']} | {row['status']} |" not in index:
            raise ValueError('Markdown/JSON registry differs: ' + row['id'])
        if row['id'] == 'MS-N000':
            continue
        path = root / row['skill']
        if not path.resolve().is_relative_to((root / 'skills/tasks').resolve()):
            raise ValueError('Task skill path escaped')
        text = path.read_text(encoding='utf-8')
        m = re.match(r'---\nname: ([a-z0-9-]{1,64})\ndescription: (.+)\n---\n', text)
        if not m or row['id'] not in text or row['title'] not in text or len(text) < 1800:
            raise ValueError('Incomplete task skill/frontmatter: ' + row['id'])
        for dependency in row['dependencies']:
            if dependency not in text:
                raise ValueError('Task skill dependency differs: ' + row['id'])
        if any(value in text for value in ['Owner:', 'Reviewer:', 'Task Approver:']):
            raise ValueError('Permanent personal assignment in new task')
        if f"[SKILL.md](../../{row['skill']})" not in index:
            raise ValueError('Task skill not discoverable from index')
        checks.append('complete linked task skill: ' + row['id'])

    retirement = json.loads((root / 'specs/maintenance/docs-workflow-dispositions.json').read_text(encoding='utf-8'))
    removed = [r['path'] for r in retirement['files'] if r['action'] == 'removed']
    expected_removed = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', retirement['base_sha'],
                                               '--', 'harness', 'specs/harness', 'tests/harness'], cwd=root).decode().splitlines()
    if set(removed) != set(expected_removed):
        raise ValueError('Retirement must cover exactly the audited40 files')
    for name in removed:
        if (root / name).exists() or (root / name).is_symlink():
            raise ValueError('Retired development Harness file exists: ' + name)
    # Git inputs exclude node_modules, venvs and generated runtime directories
    # before traversal; do not scan third-party Python files inside dependencies.
    python_inputs = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '--', '*.py'], cwd=root
    ).decode().splitlines()
    for name in python_inputs:
        path = root / name
        if not name.startswith(('backend/', 'frontend/', 'scripts/', 'tests/')) or not path.is_file():
            continue
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            imports = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module or ''] if isinstance(node, ast.ImportFrom) else []
            if any(value == 'harness' or value.startswith('harness.') for value in imports):
                raise ValueError('Runtime import of retired Harness: ' + str(path))
    checks.append('exact Harness retirement and no product/tooling imports')
    from scripts.target_verification import target_checks
    registry = target_checks()
    if len(registry) != 15 or any(row[2] == 'harness' for row in registry):
        raise ValueError('Product registry must retain15 checks without Harness')
    if not any('frontend-e2e' in row[1] for row in registry) or not any('backend-tests' in row[1] for row in registry):
        raise ValueError('Runtime checks missing')
    ci = (root / '.github/workflows/ci.yml').read_text(encoding='utf-8')
    if not ci.startswith('name: Harness verification\n') or '\n  verify:\n' not in ci:
        raise ValueError('Existing status-check identity changed')
    migration = (root / '.github/workflows/migration-ci.yml').read_text(encoding='utf-8')
    old = subprocess.check_output(['git', 'show', retirement['base_sha'] + ':.github/workflows/migration-ci.yml'], cwd=root).decode()
    if re.findall(r'^  ([a-z][a-z-]+):$', migration, re.M) != re.findall(r'^  ([a-z][a-z-]+):$', old, re.M):
        raise ValueError('Migration CI job IDs changed')
    checks.append('product registry and existing CI workflow/job identities retained')
    names = subprocess.check_output(['git', 'ls-files', '*.md'], cwd=root).decode().splitlines()
    names += [p.relative_to(root).as_posix() for p in (root / 'docs').rglob('*.md')]
    names += [p.relative_to(root).as_posix() for p in (root / 'skills/tasks').rglob('SKILL.md')]
    names += ['specs/current-contracts.md']
    checks.extend(local_links(root, sorted({n for n in names if (root / n).is_file()})))
    return checks


def main():
    try:
        checks = verify()
    except (OSError, ValueError, KeyError, SyntaxError, subprocess.SubprocessError) as exc:
        print('FAIL:', exc)
        return 1
    print('PASS', len(checks), 'queue/document/import/CI checks')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
