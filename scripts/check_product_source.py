"""Check current task/doc sources and preserved future domain requirements."""
from pathlib import Path
import argparse
import re
import subprocess
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_workflow_docs import verify as verify_workflow
from scripts.repository_history import SOURCE, repository_changes


def protected_material(text):
    """Translation may change prose, never code, identifiers in code or quantities."""
    return {
        'code': re.findall(r'(?ms)^```[^\n]*\n(.*?)^```', text),
        'inline_code': Counter(re.findall(r'(?<!`)`([^`\n]+)`(?!`)', text)),
        'quantities': Counter(re.findall(r'\d+(?:[.,]\d+)*', text)),
        'urls': Counter(re.findall(r'https?://[^\s<>\)\]"`]+', text)),
    }


def verify():
    checks = verify_workflow()
    original = subprocess.check_output(['git', 'show', SOURCE + ':docs/specifications/technical-spec-v7.2-draft.md'], cwd=ROOT).decode('utf-8')
    heads = list(re.finditer(r'(?m)^## (\d+)\.', original))
    sections = {int(m[1]): original[m.start():heads[i+1].start() if i+1 < len(heads) else len(original)].strip() for i,m in enumerate(heads)}
    current = (ROOT / 'specs/product/learning-requirements.md').read_text(encoding='utf-8')
    current_heads = list(re.finditer(r'(?m)^## (\d+)\.', current))
    current_sections = {int(m[1]): current[m.start():current_heads[i+1].start() if i+1 < len(current_heads) else len(current)].strip() for i,m in enumerate(current_heads)}
    for number in [6,7,8,9,10,11,14,15,16]:
        if number not in current_sections or protected_material(sections[number]) != protected_material(current_sections[number]):
            raise ValueError('Protected domain/security material changed in translation: section ' + str(number))
        checks.append('preserved code/quantities/references in translated requirements: ' + str(number))
    # Exact accepted Russian text is also pinned, rather than allowing arbitrary prose edits.
    from scripts.repository_history import verify_document_translations
    verify_document_translations(ROOT)
    retired = repository_changes(ROOT)
    for name in ['docs/specifications/technical-spec-v7.2-draft.md', 'specs/product/task-dispositions-v7.2.json']:
        if name not in retired or retired[name]['action'] != 'removed':
            raise ValueError('Old specification not explicitly retired: ' + name)
    checks.append('old specifications explicitly retired; current task cards authoritative')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.output and (args.output.exists() or not args.output.resolve().is_relative_to((ROOT/'var').resolve())):
        parser.error('New owned report under var/ required')
    try:
        checks = verify()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print('FAIL:', exc)
        return 1
    if args.output:
        import json
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump({'status':'PASS_SCOPED_DOCUMENTS','assertions':len(checks),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'full_target':'NOT_RUN'}, stream)
    print('PASS', len(checks), 'current-document/source checks')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
