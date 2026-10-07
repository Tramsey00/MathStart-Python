"""R01 source/inventory audit; no database writes or runtime mutations.

Run with the existing Django interpreter. The original checkout is a separate
argument; tracked input is pinned to --commit, never the audit's own manifest.
"""
import argparse
import ast
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])

def save(root, name, data):
    (root / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--original', type=Path, required=True)
    p.add_argument('--commit', required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[4]
    out = root / 'docs/acceptance/MS7-MIG-R01'
    original = args.original.resolve()
    tree = git(root, 'ls-tree', '-r', '-z', args.commit).split(b'\0')
    entries = []
    objects = []
    for row in tree:
        if not row:
            continue
        metadata, path = row.split(b'\t', 1)
        mode, kind, blob = metadata.decode().split()
        assert kind == 'blob', 'Unsupported non-blob source entry'
        objects.append(blob)
        entries.append({'path': path.decode('utf-8'), 'mode': mode, 'git_blob': blob})
    batch = subprocess.run(['git', '-C', str(root), 'cat-file', '--batch'],
                           input=('\n'.join(objects) + '\n').encode(), capture_output=True, check=True).stdout
    offset = 0
    differences = []
    for row in entries:
        end = batch.index(b'\n', offset)
        header = batch[offset:end].decode().split()
        size = int(header[2])
        data = batch[end + 1:end + 1 + size]
        offset = end + 2 + size
        row.update(size=size, sha256=sha(data))
        a, b = original / row['path'], root / row['path']
        row['original_checkout_sha256'] = sha(a.read_bytes()) if a.is_file() else None
        row['candidate_checkout_sha256'] = sha(b.read_bytes()) if b.is_file() else None
        if row['original_checkout_sha256'] != row['candidate_checkout_sha256']:
            differences.append(row['path'])
    counts = {
        'tracked_files': len(entries),
        'lesson_json': sum(x['path'].startswith('curriculum/') and x['path'].endswith('/lesson.json') for x in entries),
        'lesson_css': sum(x['path'].startswith('curriculum/') and x['path'].endswith('/page.css') for x in entries),
        'lesson_js': sum(x['path'].startswith('curriculum/') and x['path'].endswith('/page.js') for x in entries),
        'site_page_json': sum(x['path'].startswith('site_content/') and x['path'].endswith('/page.json') for x in entries),
        'templates_html': sum(x['path'].startswith('templates/') and x['path'].endswith('.html') for x in entries),
    }
    save(out, 'source-manifest.json', {'source_commit': args.commit, 'digest_semantics': 'SHA256 of exact Git blob bytes; checkout SHA256 separately records line-ending transformations. No rendered or runtime digest here. Manifest excludes itself and all R01 additions.', 'counts': counts, 'checkout_differences': differences, 'files': entries})
    preserved = []
    for prefix in ['output', 'tmp']:
        for f in sorted((original / prefix).rglob('*')):
            if f.is_file() and not f.is_symlink() and not f.is_relative_to(original / 'tmp/ms7-mig-r01'):
                preserved.append({'path': f.relative_to(original).as_posix(), 'size': f.stat().st_size, 'sha256': sha(f.read_bytes())})
    # Private preservation inventory remains in QA, not committed (may contain
    # user-created filenames); only aggregate digest/count is recorded publicly.
    private = original / 'tmp/ms7-mig-r01/qa/preservation.json'
    if private.exists():
        assert json.loads(private.read_text(encoding='utf-8')) == preserved, 'Original preserved output/tmp changed; do not overwrite evidence'
    else:
        private.write_text(json.dumps(preserved, ensure_ascii=False, indent=2), encoding='utf-8')
    references = []
    for f in sorted((original / 'docs/agent-traces').glob('*.md')):
        for value in sorted(set(re.findall(r'(?:output|tmp)/[\w./-]+', f.read_text(encoding='utf-8')))):
            target = original / value.rstrip('.')
            record = {'trace': f.relative_to(original).as_posix(), 'reference': value, 'exists': target.exists(), 'kind': 'directory' if target.is_dir() else 'file' if target.is_file() else 'missing_or_pattern'}
            if target.is_file():
                record.update(size=target.stat().st_size, sha256=sha(target.read_bytes()))
            references.append(record)
    save(out, 'historical-output-links.json', references)
    recovery = original / 'docs/agent-traces/local-runtime-recovery-20261007.md'
    save(out, 'local-delta.json', {'input_commit': args.commit, 'branch': git(original, 'branch', '--show-current').decode().strip(), 'ahead_behind': git(original, 'rev-list', '--left-right', '--count', 'HEAD...origin/main').decode().strip(), 'staged': git(original, 'diff', '--cached', '--name-only').decode().splitlines(), 'unstaged': git(original, 'diff', '--name-only').decode().splitlines(), 'classification': {'sources': 'no delta; PR27 content already in main; visual acceptance pending', 'code_tests': 'no delta; identity/grades present in input tree', 'documents_evidence': [{'path': recovery.relative_to(original).as_posix(), 'sha256': sha(recovery.read_bytes()), 'candidate_sha256': sha((root / recovery.relative_to(original)).read_bytes()), 'disposition': 'included unchanged; historical recovery evidence, not new approval'}], 'runtime_data': 'ignored .env/db.sqlite3/media/staticfiles/var retained in original; no copies or dump', 'temporary_qa': {'roots': ['output/', 'tmp/'], 'disposition': 'retained, excluded from snapshot', 'files': len(preserved), 'inventory_sha256': sha(private.read_bytes())}}, 'git_status': git(original, 'status', '--short', '--untracked-files=normal').decode().splitlines()})
    static_inventory = {}
    for area in ['templates', 'static', 'curriculum', 'site_content', 'tests', 'harness', 'scripts']:
        paths = [x['path'] for x in entries if x['path'].startswith(area + '/')]
        static_inventory[area] = {'files': paths, 'suffix_counts': dict(Counter(Path(x).suffix for x in paths))}
    commands = []
    for f in sorted((root / 'content/management/commands').glob('*.py')):
        if f.name == '__init__.py':
            continue
        text = f.read_text(encoding='utf-8')
        commands.append({'path': f.relative_to(root).as_posix(), 'arguments': re.findall(r'add_argument\(\s*["\']([^"\']+)', text), 'help': re.findall(r'help\s*=\s*["\']([^"\']+)', text)})
    static_inventory['management_commands'] = commands
    static_inventory['test_cases'] = []
    for x in entries:
        if Path(x['path']).name.startswith('test') and x['path'].endswith('.py'):
            module = ast.parse((root / x['path']).read_text(encoding='utf-8-sig'))
            static_inventory['test_cases'].append({'path': x['path'], 'tests': [n.name for n in ast.walk(module) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_')]})
    save(out, 'file-inventory.json', static_inventory)
    print(json.dumps({'counts': counts, 'checkout_differences': differences, 'preserved_files': len(preserved), 'historical_references': len(references)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
