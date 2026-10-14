"""R03 orchestration for a real published V02 commit, never a staged surrogate."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'Tramsey00/MathStart-Python'
BASE = '0c03197e23f69a233c0fcf8bdffa336feca20b92'
TREE = 'dbad1e853dff354c5d3255755afb5cc32e0ad279'
CONTROL = '1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68'
ANCHOR = '5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7'
CONFIRMATION_PATH = 'docs/acceptance/MS7-MIG-R03/v02-publication-20261014/owner-confirmation.json'
CONFIRMATION_SHA = '0a872e5f2c15fd6e6e031c87c97e6ca41323db4bdfa84da60383978319e3a8f4'
INPUT_PATH = 'specs/migration/r03-v1/v02-published-candidate.json'
OWNER_FILES = {
    'scripts/v02_publication_gate.py': '8235b72cc34b60b4eae1da2ced1b7d705000fbecd4fa6f93f36be16825215f49',
    'scripts/v02_publication_intake.py': 'ce17cd0814b37d0c208279719bb945324e097aa50ad80e27715796e63f2cadd8',
}


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'DUPLICATE_JSON_KEY: '+key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(value, sort_keys=True, indent=2)+'\n').encode())


def confirmation(raw):
    require(sha(raw) == CONFIRMATION_SHA, 'HUMAN_CONFIRMATION_DIGEST')
    decision = decode(raw)
    require(decision['publication_authorized'] is True and
            decision['trusted_control_revision'] == CONTROL and
            decision['confirmed_anchor_sha256'] == ANCHOR and
            decision['authorized_candidate_parent'] == BASE and
            decision['authorized_candidate_tree'] == TREE, 'HUMAN_CONFIRMATION_SCOPE')
    return decision


def candidate_input(raw):
    data = decode(raw)
    expected = {'format', 'task_id', 'status', 'pr_url', 'implementation_sha',
                'control_revision', 'anchor_sha256', 'owner_confirmation_sha256'}
    require(set(data) == expected, 'CANDIDATE_INPUT_SCHEMA')
    require(data['format'] == 'r03-v02-published-candidate-v1' and
            data['task_id'] == 'MS7-MIG-V02' and data['status'] == 'PINNED_PUBLISHED_CANDIDATE',
            'PUBLISHED_CANDIDATE_REQUIRED')
    require(isinstance(data['implementation_sha'], str) and
            re.fullmatch('[0-9a-f]{40}', data['implementation_sha']) is not None,
            'FULL_IMPLEMENTATION_SHA_REQUIRED')
    require(data['implementation_sha'] not in (BASE, TREE, CONTROL), 'SURROGATE_IMPLEMENTATION_FORBIDDEN')
    require(data['control_revision'] == CONTROL and data['anchor_sha256'] == ANCHOR and
            data['owner_confirmation_sha256'] == CONFIRMATION_SHA, 'CANDIDATE_CANNOT_OVERRIDE_TRUST_PINS')
    require(isinstance(data['pr_url'], str), 'EXACT_REPOSITORY_PR_URL_REQUIRED')
    match = re.fullmatch(r'https://github\.com/Tramsey00/MathStart-Python/pull/([1-9][0-9]*)', data['pr_url'])
    require(match is not None, 'EXACT_REPOSITORY_PR_URL_REQUIRED')
    data['pr_number'] = int(match.group(1))
    return data


def validate_pr(pr, data):
    require(pr['number'] == data['pr_number'] and pr['state'] == 'open' and not pr.get('merged'), 'CURRENT_OPEN_PR_REQUIRED')
    require(pr['user']['login'] == 'VladimirFrolov777' and 'MS7-MIG-V02' in pr['title'], 'V02_OWNER_TASK_PR_REQUIRED')
    require(pr['head']['repo']['full_name'] == REPOSITORY and
            pr['base']['repo']['full_name'] == REPOSITORY and
            pr['base']['ref'] == 'ms7-mig-react-fastapi', 'CANDIDATE_REPOSITORY_BASE')
    require(pr['head']['sha'] == data['implementation_sha'], 'LIVE_PR_HEAD_CHANGED')
    require(pr['base']['sha'] == BASE, 'LIVE_PR_BASE_CHANGED')


def validate_commit(commit, data):
    require(commit['sha'] == data['implementation_sha'], 'IMPLEMENTATION_COMMIT_SHA')
    require([p['sha'] for p in commit['parents']] == [BASE], 'IMPLEMENTATION_SINGLE_BASE_PARENT')
    require(commit['tree']['sha'] == TREE, 'IMPLEMENTATION_TREE_PIN')


def fetch_json(path, output, name):
    url = 'https://api.github.com/repos/'+REPOSITORY+'/'+path
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'MathStart-R03-published-V02',
               'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = 'Bearer '+token
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        raw = response.read(2_000_001)
        require(len(raw) <= 2_000_000, 'GITHUB_RESPONSE_BOUND')
        status = response.status
    (output/(name+'.raw.json')).write_bytes(raw)
    save(output/(name+'.receipt.json'), dict(url=url, status=status, sha256=sha(raw), bytes=len(raw), timeout_seconds=30))
    return decode(raw)


def checked_owner_module(owner):
    require(owner.is_dir() and not owner.is_symlink() and not owner.is_relative_to(ROOT), 'SEPARATE_OWNER_CHECKOUT_REQUIRED')
    # Both scripts are checked before loading any code from the owner checkout.
    checked_bytes = {}
    for path, digest in OWNER_FILES.items():
        file = owner/path
        require(file.is_file() and not file.is_symlink(), 'APPROVED_OWNER_EXECUTABLE_TYPE: '+path)
        raw = file.read_bytes()
        require(sha(raw) == digest,
                'APPROVED_OWNER_EXECUTABLE_DIGEST: '+path)
        checked_bytes[path] = raw
    require(not (owner/'scripts/__pycache__').exists() and
            not (owner/'scripts/v02_publication_intake.pyc').exists(), 'UNAPPROVED_OWNER_BYTECODE')
    spec = importlib.util.spec_from_file_location('approved_r03_intake', owner/'scripts/v02_publication_intake.py')
    module = importlib.util.module_from_spec(spec)
    # Execute the bytes just hashed, without reading a cached .pyc or reopening
    # the source through a loader. The approved older gate also starts cache-free.
    exec(compile(checked_bytes['scripts/v02_publication_intake.py'], str(owner/'scripts/v02_publication_intake.py'), 'exec'), module.__dict__)
    return module


def execute(owner, output, orchestrator_sha):
    decision = confirmation((ROOT/CONFIRMATION_PATH).read_bytes())
    path = ROOT/INPUT_PATH
    require(path.is_file(), 'NOT_RUN_PUBLISHED_PR_AND_IMPLEMENTATION_SHA_NOT_RECEIVED')
    raw_input = path.read_bytes()
    data = candidate_input(raw_input)
    require(re.fullmatch('[0-9a-f]{40}', orchestrator_sha) is not None, 'FULL_ORCHESTRATOR_REVISION_REQUIRED')
    owner_module = checked_owner_module(owner)
    runner = owner_module.Runner(output/'orchestrator-raw')
    require(runner.git(ROOT, 'rev-parse', 'HEAD').decode().strip() == orchestrator_sha, 'ORCHESTRATOR_CHECKOUT_SHA')
    for path in [INPUT_PATH, CONFIRMATION_PATH, 'scripts/published_v02_ci.py']:
        require((ROOT/path).read_bytes() == runner.git(ROOT, 'show', orchestrator_sha+':'+path), 'DIRTY_ORCHESTRATOR_INPUT: '+path)
    require(runner.git(owner, 'rev-parse', 'HEAD').decode().strip() == CONTROL, 'OWNER_CHECKOUT_REVISION')
    runner.run('python-version', [sys.executable, '-I', '-B', '--version'], output)
    runner.git(output, '--version')
    pr_before = fetch_json('pulls/'+str(data['pr_number']), output, 'pr-before')
    validate_pr(pr_before, data)
    commit = fetch_json('git/commits/'+data['implementation_sha'], output, 'commit-before')
    validate_commit(commit, data)
    # New disposable repository, approved stdlib/Git only. No candidate code,
    # hooks, dependency scripts, worktrees or databases are executed/modified.
    candidate = output/'candidate'
    require(not candidate.exists(), 'FRESH_CANDIDATE_DIRECTORY_REQUIRED')
    candidate.mkdir()
    runner.git(candidate, 'init', '--template=', '--initial-branch=r03-published-check')
    runner.git(candidate, 'config', 'core.filemode', 'true')
    runner.git(candidate, 'remote', 'add', 'origin', 'https://github.com/'+REPOSITORY+'.git')
    runner.git(candidate, 'fetch', '--no-tags', '--depth=2', 'origin', data['implementation_sha'])
    actual_head = runner.git(candidate, 'rev-parse', 'FETCH_HEAD').decode().strip()
    require(actual_head == data['implementation_sha'], 'FETCHED_IMPLEMENTATION_SHA')
    runner.git(candidate, 'update-ref', 'HEAD', actual_head)
    actual_tree = runner.git(candidate, 'rev-parse', actual_head+'^{tree}').decode().strip()
    parents = runner.git(candidate, 'show', '-s', '--format=%P', actual_head).decode().strip().split()
    validate_commit(dict(sha=actual_head, tree={'sha': actual_tree}, parents=[{'sha': p} for p in parents]), data)
    runner.git(candidate, 'read-tree', actual_head)
    runner.git(candidate, 'checkout-index', '--all')
    runner.git(candidate, 'fsck', '--full', '--no-reflogs')
    before_receipt = dict(implementation_sha=data['implementation_sha'], pr_url=data['pr_url'],
                          live_pr_head_before=pr_before['head']['sha'], actual_checkout_sha=actual_head,
                          actual_checkout_tree=actual_tree, actual_parents=parents,
                          control_revision=CONTROL, actual_control_checkout_sha=CONTROL,
                          workflow_sha=os.environ.get('GITHUB_WORKFLOW_SHA', orchestrator_sha),
                          orchestrator_revision_sha=orchestrator_sha,
                          workflow_event_sha=os.environ.get('GITHUB_SHA'),
                          owner_confirmation_sha256=CONFIRMATION_SHA, owner_anchor_sha256=ANCHOR,
                          input_sha256=sha(raw_input), representation='PUBLISHED_COMMIT',
                          publication_authorized=decision['publication_authorized'])
    save(output/'checkout-provenance.json', before_receipt)
    argv = [sys.executable, '-I', '-B', owner/'scripts/v02_publication_gate.py', 'published',
            '--owner-revision', CONTROL, '--root', candidate, '--ref', data['implementation_sha'],
            '--output', output/'gate']
    # Recheck executable identity immediately before spawning the approved gate.
    checked_owner_module(owner)
    runner.run('published-gate', argv, owner, timeout=600)
    gate = decode((output/'gate/result.json').read_bytes())
    require(gate['result'] == 'PASS' and gate['representation'] == 'published-commit' and
            gate['implementation_sha'] == actual_head and gate['actual_checkout_sha'] == actual_head and
            gate['tree'] == TREE and gate['owner_control_revision'] == CONTROL and gate['anchor_sha256'] == ANCHOR,
            'PUBLISHED_GATE_RECEIPT')
    pr_after = fetch_json('pulls/'+str(data['pr_number']), output, 'pr-after')
    validate_pr(pr_after, data)
    before_receipt.update(result='PASS_PUBLISHED_COMMIT_GATE', live_pr_head_after=pr_after['head']['sha'],
                          v02_task_approval=False, merge_performed=False, issues_closed=False,
                          r03_status='INCOMPLETE', run_id=os.environ.get('GITHUB_RUN_ID'),
                          note='Approved older gate receipt labels are preserved. Current publication authorization is this separate human-confirmation record.')
    save(output/'published-result.json', before_receipt)
    return before_receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--orchestrator-revision', required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    require(not output.exists(), 'NEW_EVIDENCE_DIRECTORY_REQUIRED')
    require(not output.is_relative_to(args.owner.resolve()), 'EVIDENCE_OUTSIDE_OWNER_CHECKOUT_REQUIRED')
    output.mkdir(parents=True)
    try:
        result = execute(args.owner.resolve(), output, args.orchestrator_revision)
        print(json.dumps(result, indent=2))
    except Exception as error:
        save(output/'failure.json', dict(result='FAIL_OR_NOT_RUN', error=str(error),
                                        publication_authorized=True, task_approval=False, r03_status='INCOMPLETE'))
        raise
    finally:
        rows = [dict(path=p.relative_to(output).as_posix(), bytes=p.stat().st_size, sha256=sha(p.read_bytes()))
                for p in output.rglob('*') if p.is_file() and 'candidate' not in p.relative_to(output).parts]
        save(output/'publication-evidence-manifest.json', rows)


if __name__ == '__main__':
    main()
