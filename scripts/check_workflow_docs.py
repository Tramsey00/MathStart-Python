"""Read-only checks for the current tasks, complete lesson inventory and local links."""
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


def validate_queue(data, source=None):
    rows = data['tasks']
    ids = [r['id'] for r in rows]
    if not rows or len(set(ids)) != len(ids) or [r['order'] for r in rows] != list(range(len(rows))):
        raise ValueError('Queue IDs/order must be unique and consecutive')
    position = {value: i for i, value in enumerate(ids)}
    for row in rows:
        if row['status'] not in STATUSES or not row.get('acceptance') or not row.get('title'):
            raise ValueError('Missing task status/title/acceptance: ' + row['id'])
        if len(row['dependencies']) != len(set(row['dependencies'])):
            raise ValueError('Duplicate dependency: ' + row['id'])
        for dependency in row['dependencies']:
            if dependency not in position or position[dependency] >= position[row['id']]:
                raise ValueError('Missing, cyclic or forward dependency: ' + row['id'])
            if rows[position[dependency]]['status'] == 'REMOVED_FROM_PLAN':
                raise ValueError('Dependency on retired task: ' + row['id'])
    return rows


def validate_workflow(data):
    expected = {'MS-T001', 'MS-T002', 'MS-T002A'}
    policy = data['workflow']
    bootstrap = policy['bootstrap']
    regular = policy['regular']
    if set(bootstrap['tasks']) != expected or len(bootstrap['tasks']) != 3:
        raise ValueError('Bootstrap exception must cover exactly three tasks')
    if bootstrap['branch'] != 'ui/ux' or bootstrap['issue_required'] or bootstrap['separate_branch_required']:
        raise ValueError('Bootstrap must reuse ui/ux without per-task Issue/branch')
    if regular['starts_at'] != 'MS-T003' or not all(regular[k] for k in ['issue_required', 'branch_required', 'pull_request']):
        raise ValueError('Regular tasks require Issue, branch and PR')
    if not {'codex/', '/codex'}.issubset(regular['forbidden_prefixes']):
        raise ValueError('Forbidden branch prefixes missing')
    rows = {r['id']: r for r in data['tasks']}
    if rows['MS-T002A']['dependencies'] != ['MS-T002'] or rows['MS-T003']['dependencies'] != ['MS-T002A']:
        raise ValueError('Team clone/start handoff must precede grade migration')
    for row in rows.values():
        expected_mode = 'bootstrap' if row['id'] in expected else 'preparation' if row['id'] == 'MS-T000' else 'regular'
        if row.get('workflow') != expected_mode:
            raise ValueError('Task workflow differs: ' + row['id'])


def local_links(root, documents):
    """Validate actual links; frozen source links may resolve to explicitly retired Git blobs."""
    from scripts.check_migration_preservation import dispositions, historical_artifact
    historical = dispositions(root)
    from scripts.repository_history import repository_changes
    retired = repository_changes(root)
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
                if name.startswith(('specs/', 'docs/adr/')) and (key in historical or key in retired):
                    historical_artifact(key, root)
                else:
                    raise ValueError('Broken local link: ' + name + ' -> ' + target)
            checks.append('local link: ' + name + ' -> ' + target)
    return checks


def verify(root=ROOT):
    queue = json.loads((root / 'docs/tasks/registry.json').read_text(encoding='utf-8'))
    rows = validate_queue(queue)
    if queue.get('version') != 2:
        raise ValueError('Expected current task registry v2')
    validate_workflow(queue)
    index = (root / 'docs/tasks/INDEX.md').read_text(encoding='utf-8')
    checks = ['queue unique/order/dependencies/no cycles']
    skills = set()
    for row in rows:
        if f"| {row['order']:02} | {row['id']} — {row['title']} | {row['status']} |" not in index:
            raise ValueError('Markdown/JSON registry differs: ' + row['id'])
        path = root / row['skill']
        if not path.resolve().is_relative_to((root / 'skills/tasks').resolve()) or path in skills:
            raise ValueError('Task skill escaped or duplicated')
        skills.add(path)
        text = path.read_text(encoding='utf-8')
        if not re.match(r'---\nname: [a-z0-9-]{1,64}\ndescription: .+\n---\n', text):
            raise ValueError('Invalid task skill frontmatter: ' + row['id'])
        if row['id'] not in text or row['title'] not in text:
            raise ValueError('Task skill identity differs: ' + row['id'])
        if any(dependency not in text for dependency in row['dependencies']):
            raise ValueError('Task skill dependency differs: ' + row['id'])
        if any(value in text for value in ['Owner:', 'Reviewer:', 'Task Approver:']):
            raise ValueError('Permanent personal assignment in task')
        if f"[SKILL.md](../../{row['skill']})" not in index:
            raise ValueError('Task skill not discoverable')
        checks.append('linked task skill: ' + row['id'])
    if set((root / 'skills/tasks').glob('*/SKILL.md')) != skills:
        raise ValueError('Unregistered active task skill')
    inventory = json.loads((root / 'docs/tasks/lesson-inventory.json').read_text(encoding='utf-8'))['topics']
    by_slug = {r['slug']: r for r in inventory}
    if len(by_slug) != len(inventory):
        raise ValueError('Duplicate inventory slug')
    actual = {}
    for metadata in (root / 'curriculum').rglob('lesson.json'):
        page = json.loads(metadata.read_text(encoding='utf-8'))['page']
        if page.get('is_published') and page.get('page_type') == 'topic':
            actual[page['slug']] = dict(page, source=metadata.parent.relative_to(root).as_posix())
    if set(actual) != set(by_slug):
        raise ValueError('Published lesson inventory incomplete')
    urls = [r['assigned_path'] for r in inventory if r['assigned_path'] is not None]
    if len(urls) != len(set(urls)):
        raise ValueError('Duplicate assigned lesson URL')
    for slug, row in by_slug.items():
        if any(row[k] != actual[slug][k] for k in ['grade', 'subject', 'section', 'title', 'order', 'source']):
            raise ValueError('Lesson inventory metadata differs: ' + slug)
    for row in rows:
        if row.get('grade'):
            count = sum(r['grade'] == row['grade'] for r in inventory)
            if count != row['expected_topics'] or row['inventory'] != 'docs/tasks/lesson-inventory.json':
                raise ValueError('Class task inventory differs: ' + row['id'])
    checks.append('complete lesson inventory and class scopes')
    python_inputs = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '--', '*.py'], cwd=root).decode().splitlines()
    for name in python_inputs:
        path = root / name
        if not name.startswith(('backend/', 'frontend/', 'scripts/', 'tests/')) or not path.is_file():
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8-sig'))):
            imports = [x.name for x in node.names] if isinstance(node, ast.Import) else [node.module or ''] if isinstance(node, ast.ImportFrom) else []
            if any(value == 'harness' or value.startswith('harness.') for value in imports):
                raise ValueError('Runtime import of retired Harness: ' + name)
    for directory in ['harness', 'specs/harness', 'tests/harness']:
        if (root / directory).exists():
            raise ValueError('Retired Harness directory reintroduced')
    checks.append('no retired Harness files/imports')
    ci = (root / '.github/workflows/ci.yml').read_text(encoding='utf-8')
    if not ci.startswith('name: Product verification\n') or '\n  verify:\n' not in ci:
        raise ValueError('Product workflow or verify job changed')
    from scripts.target_verification import target_checks
    registry = target_checks()
    if len(registry) != 15 or not any('frontend-e2e' in r[1] for r in registry) or not any('backend-tests' in r[1] for r in registry):
        raise ValueError('Product runtime check registry changed')
    checks.append('existing product checks retained')
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '--', '*.md'], cwd=root).decode().splitlines()
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
