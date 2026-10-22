"""Reconcile immutable source history and the current, explicitly changed product draft."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.historical_sources import retired_bytes, retired_json

BASE = '1a015f7513933901e8bb252e94c660e4383b6b0e'
SOURCE_REGISTRY = 'specs/product/task-dispositions-v7.2.json'
SPEC = 'docs/specifications/technical-spec-v7.2-draft.md'


def blob(sha, name):
    return subprocess.check_output(['git', 'show', sha + ':' + name], cwd=ROOT).decode('utf-8')


def edges(body):
    out = set()
    for kind, nxt in [('HARD', 'CONTRACT'), ('CONTRACT', 'HANDOFF'),
                      ('HANDOFF', 'INTEGRATION'), ('INTEGRATION', 'Что можно делать параллельно')]:
        m = re.search(kind + ':(.*?)' + nxt + ':', body, re.S)
        if not m:
            raise ValueError('Missing source dependency type: ' + kind)
        for token in re.findall(r'MS[67]-?[RVI]\d{2}[AB]?|(?<![\w-])R0[23](?!\w)', m[1]):
            out.add((kind, re.sub(r'^(MS[67])(?=[RVI])', r'\1-', token)))
    return out


def chapters(text):
    heads = list(re.finditer(r'(?m)^## (\d+)\.', text))
    return {int(m[1]): text[m.start(): heads[i + 1].start() if i + 1 < len(heads) else len(text)].strip()
            for i, m in enumerate(heads)}


def verify():
    checks = []

    def check(ok, label):
        if not ok:
            raise ValueError(label)
        checks.append(label)

    spec = (ROOT / SPEC).read_text(encoding='utf-8')
    registry = json.loads((ROOT / SOURCE_REGISTRY).read_text(encoding='utf-8'))
    audit = retired_json('docs/acceptance/migration-execution/product-source-audit.json')
    previous = json.loads(blob(BASE, SOURCE_REGISTRY))
    historical_spec = blob(BASE, SPEC)
    original = json.loads(blob('953fe979742784a196efab203ab987c0cfefd3b3',
                              'docs/acceptance/migration-execution/product-task-disposition-draft.json'))
    check(hashlib.sha256(retired_bytes(registry['source_pdf'])).hexdigest() ==
          registry['source_pdf_sha256'] == audit['source_pdf_sha256'], 'original PDF hash unchanged')
    check([int(x) for x in re.findall(r'(?m)^## (\d+)\.', spec)] == list(range(1, 33)),
          'current full draft has all32 chapters once in order')
    current_ids = re.findall(r'(?m)^### (MS7-[RVI]\d{2}[AB]?)\s*·', spec)
    check(len(current_ids) == len(set(current_ids)) == 52 and
          set(current_ids) == {r['id'] for r in registry['rows']}, 'current52 disposition headings unique and complete')
    check(len(registry['rows']) == len({r['id'] for r in registry['rows']}) == 52,
          'source registry unique52 IDs')
    old_heads = list(re.finditer(r'(?m)^### (MS7-[RVI]\d{2}[AB]?)\s*·[^\n]*', historical_spec))
    check(len(old_heads) == 52, 'pinned previous full52 cards available')
    for i, m in enumerate(old_heads):
        row = next(r for r in registry['rows'] if r['id'] == m[1])
        prior = next(r for r in previous['rows'] if r['id'] == m[1])
        original_row = next(r for r in original['rows'] if r['id'] == m[1])
        body = historical_spec[m.end():old_heads[i + 1].start() if i + 1 < len(old_heads)
                               else historical_spec.index('## 25.')]
        expected = {(d['kind'], d['id']) for d in row['dependencies']}
        check(edges(body) == edges(row['source_card_text']) == expected,
              m[1] + ' historical typed edges equal PDF/source/pinned full card')
        check(hashlib.sha256(row['source_card_text'].encode()).hexdigest() == row['source_card_text_sha256'],
              m[1] + ' complete source excerpt hash')
        # Every pre-existing field is immutable. Workflow is added separately.
        check(all(row.get(k) == v for k, v in prior.items()), m[1] + ' all prior source/results/approvals preserved')
        check(all(row.get(k) == original_row.get(k) for k in
                  ['original_result', 'original_result_source', 'current_acceptance_reconciliation',
                   'dependencies', 'current_status', 'platform_disposition']),
              m[1] + ' original accepted source snapshot retained')
    check(sum(len(r['dependencies']) for r in registry['rows']) == 115, 'all115 historical typed edges retained')
    check(dict(collections.Counter(d['kind'] for r in registry['rows'] for d in r['dependencies'])) ==
          registry['source_dependency_audit']['by_kind'], 'source edge kinds exact60/24/6/25')
    check(sum(r['platform_disposition'] == 'PLANNED_EQUIVALENT' and r['current_status'] == 'PLANNED'
              and not r['target_evidence'] for r in registry['rows']) == 47,
          'historical47 planned results not fabricated as implementation')
    for fix in audit['operator_repairs']:
        check(re.sub(r'[\s≤≥→#]', '', fix['old']) == re.sub(r'[\s≤≥→#]', '', fix['new']) and
              fix['new'] in historical_spec, 'historical glyph-position-only repair at source line' + str(fix['line']))
    # Current source-of-truth checks complement (not replace) historical evidence.
    # The six complete mathematical/domain/API chapters were not rewritten.
    current_chapters, prior_chapters = chapters(spec), chapters(historical_spec)
    for number in range(6, 12):
        check(current_chapters[number] == prior_chapters[number],
              f'current full chapter{number} data/exercise/knowledge/math/tutor/HTTP requirements unchanged')
    provenance = (ROOT / 'docs/specifications/technical-spec-v7.2-provenance.md').read_text(encoding='utf-8')
    for name in [SPEC, SOURCE_REGISTRY]:
        check(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() in provenance, name + ' current provenance hash')
    from scripts.check_workflow_docs import verify as workflow_verify
    checks.extend(workflow_verify())
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and (args.output.exists() or not args.output.resolve().is_relative_to((ROOT / 'var').resolve())):
        parser.error('New owned report under var/ required')
    started = datetime.now(timezone.utc).isoformat()
    try:
        checks = verify()
    except (OSError, ValueError, AssertionError, subprocess.SubprocessError) as exc:
        print('FAIL:', exc)
        return 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        report = {'status': 'PASS_SCOPED_DOCUMENT_SOURCE_RECONCILIATION', 'assertions': len(checks),
                  'case_ids': checks, 'base_sha': BASE, 'head': subprocess.check_output(
                      ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  'tree_state': 'see candidate file manifest/execution record',
                  'full_target': 'NOT_ESTABLISHED_BY_DOCUMENT_CHECKS', 'formal_acceptance': 'HUMAN_PENDING',
                  'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(), 'exit_code': 0}
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('PASS', len(checks), 'historical-source/current-document checks')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
