"""Additive R03 delta envelope; never re-pin the original publication-v3 anchor."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import types
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = '76d8eac6387a5fde5432a0e8130a881cb6d7ba82'
PREDECESSOR_TREE = 'dbad1e853dff354c5d3255755afb5cc32e0ad279'
BASE = '0c03197e23f69a233c0fcf8bdffa336feca20b92'
CONTROL = '1b75c6e58ecdcb4bb172d4df979e9b9efa7dde68'
ANCHOR = '5a9a7a65dab43afe4e353b51523d86f3a15de2e371d19efacc8127ae6d0dbfd7'
LIBRARY_SHA = '4e85a7ecb2aacae740caca75a1bf42b5eef36ae30e28897dd7125de8c663fdaa'
PINS_SHA = 'eb32a3245275649e9a69c67ea17001cfd4b8ff0cd7a30e63bcac325692c9c591'
PREDECESSOR_CASES_SHA = '681652fe986644e369a0c9cb43ac26ba8c7431a6bbae28d86e721fcd3c31da18'


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def decode(raw):
    def pairs(items):
        d = {}
        for k, v in items:
            require(k not in d, 'DUPLICATE_KEY')
            d[k] = v
        return d
    return json.loads(raw, object_pairs_hook=pairs)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, indent=2, sort_keys=True)+'\n').encode())


def hexpin(value, length):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{'+str(length)+'}', value) is not None


def safe_path(value):
    return (isinstance(value, str) and value and not PurePosixPath(value).is_absolute()
            and '\\' not in value and ':' not in value and not any(ord(c)<32 for c in value)
            and all(p not in ('', '.', '..', '.git', '.gitattributes') for p in value.split('/')))


def allowed_path(path):
    # A ceiling, not an approval: each exact patch/blob still needs independent R03 review.
    return safe_path(path) and (path in {'backend/content/releases.py', 'backend/content/projection.py',
        'backend/infrastructure/http/app.py', 'backend/infrastructure/http/README.md'}
        or (path.startswith('backend/tests/v02/') and path.endswith('.py'))
        or (path.startswith('docs/acceptance/MS7-MIG-V02/') and '/history/' not in path
            and '/publication-byte-audit/' not in path))


def reviewed_scope(raw, digest):
    require(hexpin(digest,64) and sha(raw)==digest, 'INDEPENDENT_SCOPE_DIGEST')
    d = decode(raw)
    require(d.get('status')=='REVIEWED_BY_R03', 'NOT_READY_REVIEWED_DIFF_AND_INPUTS_REQUIRED')
    fields = {'format','status','pr_number','predecessor_sha','predecessor_tree','base_sha',
              'control_revision','anchor_sha256','implementation_sha','tree_sha','patch_sha256',
              'changes','renderer_contract','owner_handoff','v02_case_ids'}
    require(set(d)==fields and d['format']=='r03-v02-successor-reviewed-v1' and d['pr_number']==53, 'SCOPE_SCHEMA')
    require((d['predecessor_sha'],d['predecessor_tree'],d['base_sha'],d['control_revision'],d['anchor_sha256'])
            == (PREDECESSOR,PREDECESSOR_TREE,BASE,CONTROL,ANCHOR), 'HISTORICAL_PINS_IMMUTABLE')
    require(hexpin(d['implementation_sha'],40) and d['implementation_sha'] not in (PREDECESSOR,BASE,CONTROL)
            and hexpin(d['tree_sha'],40) and d['tree_sha']!=PREDECESSOR_TREE and hexpin(d['patch_sha256'],64), 'EXACT_NEW_PINS_REQUIRED')
    require(isinstance(d['changes'],list) and d['changes'], 'NONEMPTY_REVIEWED_DIFF')
    paths = []
    for row in d['changes']:
        require(set(row)=={'path','before','after','attributes_sha256'} and allowed_path(row['path']), 'SCOPED_PATH')
        paths.append(row['path'])
        for key in ('before','after'):
            b = row[key]
            if key=='before' and b is None:
                continue
            require(isinstance(b,dict) and set(b)=={'oid','mode','size','sha256'} and b['mode']=='100644'
                    and hexpin(b['oid'],40) and hexpin(b['sha256'],64) and type(b['size']) is int
                    and b['size']>=0, 'REGULAR_EXACT_BLOB_REQUIRED')
        require(hexpin(row['attributes_sha256'],64), 'EXACT_ATTRIBUTES_PIN')
    require(len(paths)==len(set(paths))==len(set(p.casefold() for p in paths)), 'DUPLICATE_CHANGED_PATH')
    for key in ('renderer_contract','owner_handoff'):
        r = d[key]
        require(isinstance(r,dict) and set(r)=={'path','sha256'} and safe_path(r['path'])
                and r['path'].startswith('docs/acceptance/MS7-MIG-R03/') and hexpin(r['sha256'],64), 'R03_REVIEWED_HANDOFF_REQUIRED')
    require(isinstance(d['v02_case_ids'],list) and len(d['v02_case_ids'])>=86
            and all(isinstance(n,str) and n.startswith('backend.tests.v02.') for n in d['v02_case_ids'])
            and len(set(d['v02_case_ids']))==len(d['v02_case_ids']), 'EXACT_CASE_INVENTORY_REQUIRED')
    return d


def chain(new, predecessor, scope):
    require(new['sha']==scope['implementation_sha'] and new['tree']['sha']==scope['tree_sha'], 'NEW_COMMIT_OR_TREE_PIN')
    require([r['sha'] for r in new['parents']]==[PREDECESSOR], 'SUCCESSOR_SINGLE_PREDECESSOR_PARENT')
    require(predecessor['sha']==PREDECESSOR and predecessor['tree']['sha']==PREDECESSOR_TREE
            and [r['sha'] for r in predecessor['parents']]==[BASE], 'ORIGINAL_HISTORY_CHANGED')


def same_delta(before, after, rows):
    changed = {p for p in set(before)|set(after) if before.get(p)!=after.get(p)}
    require(changed=={r['path'] for r in rows}, 'EXACT_CHANGED_PATH_SET')
    for row in rows:
        p = row['path']
        require(before.get(p)==row['before'] and after.get(p)==row['after'], 'REVIEWED_BLOB_METADATA: '+p)


def library():
    path = ROOT/'scripts/published_v02_ci.py'
    raw = path.read_bytes()
    require(sha(raw)==LIBRARY_SHA, 'TRUSTED_LIBRARY_BYTES')
    module = types.ModuleType('r03_successor_publication')
    module.__file__ = str(path)
    exec(compile(raw,str(path),'exec'),module.__dict__)
    return module


def tree(runner, root, ref):
    result = {}
    raw = runner.git(root,'ls-tree','-rz',ref)
    for part in raw.split(b'\0'):
        if part:
            info,path = part.split(b'\t',1)
            mode,kind,oid = info.decode().split()
            result[path.decode()] = (mode,kind,oid)
    return result


def blob(runner,root,entry):
    if entry is None:
        return None
    mode,kind,oid = entry
    require(kind=='blob' and mode=='100644','REGULAR_BLOB_ONLY')
    raw = runner.git(root,'cat-file','blob',oid)
    return dict(oid=oid,mode=mode,size=len(raw),sha256=sha(raw))


def fresh(runner, output, ref):
    require(not output.exists(),'NEW_LINUX_CHECKOUT_REQUIRED')
    output.mkdir()
    runner.git(output,'init','--template=','--initial-branch=r03-successor-check')
    runner.git(output,'config','core.filemode','true')
    runner.git(output,'remote','add','origin','https://github.com/Tramsey00/MathStart-Python.git')
    runner.git(output,'fetch','--no-tags','--depth=3','origin',ref)
    require(runner.git(output,'rev-parse','FETCH_HEAD').decode().strip()==ref,'FETCHED_REF_PIN')
    runner.git(output,'update-ref','HEAD',ref)
    runner.git(output,'read-tree',ref)
    runner.git(output,'checkout-index','--all')
    require(runner.git(output,'rev-parse','HEAD').decode().strip()==ref,'ACTUAL_CHECKOUT_HEAD')
    runner.git(output,'fsck','--full','--no-reflogs')


def execute(scope_path, digest, owner_revision, controls, output):
    # Pending/unpublished pins fail before networking, control loading or candidate execution.
    raw = scope_path.read_bytes()
    data = reviewed_scope(raw,digest)
    require(hexpin(owner_revision,40) and scope_path.is_relative_to(ROOT), 'R03_OWNER_REVISION_AND_SCOPE')
    require(sys.platform=='linux','FRESH_LINUX_REQUIRED')
    publication = library()
    approved = publication.checked_owner_module(controls)
    runner = approved.Runner(output/'raw')
    require(runner.git(ROOT,'rev-parse','HEAD').decode().strip()==owner_revision,'ACTUAL_R03_CHECKOUT_REVISION')
    for p in [scope_path,Path(__file__).resolve(),ROOT/'scripts/published_v02_ci.py']:
        require(p.read_bytes()==runner.git(ROOT,'show',owner_revision+':'+p.relative_to(ROOT).as_posix()),'DIRTY_R03_CONTROL')
    require(runner.git(controls,'rev-parse','HEAD').decode().strip()==CONTROL,'ORIGINAL_CONTROL_CHECKOUT')
    for key in ('renderer_contract','owner_handoff'):
        r = data[key];p = ROOT/r['path']
        require(p.is_file() and not p.is_symlink() and sha(p.read_bytes())==r['sha256']
                and p.read_bytes()==runner.git(ROOT,'show',owner_revision+':'+r['path']),'REVIEWED_HANDOFF_BYTES')
    old_case_path = ROOT/'docs/acceptance/MS7-MIG-R03/v02-review-20261015/38642117604-v02-tests.json'
    require(sha(old_case_path.read_bytes())==PREDECESSOR_CASES_SHA,'ORIGINAL_CASE_RECEIPT_IMMUTABLE')
    old_cases = decode(old_case_path.read_bytes())
    require({r['id'] for r in old_cases['cases']}<=set(data['v02_case_ids']),'ORIGINAL_CASES_REMOVED')
    pr = publication.fetch_json('pulls/53',output,'pr-before')
    publication.validate_pr(pr,dict(pr_number=53,implementation_sha=data['implementation_sha']))
    new = publication.fetch_json('git/commits/'+data['implementation_sha'],output,'new-commit')
    old = publication.fetch_json('git/commits/'+PREDECESSOR,output,'predecessor-commit')
    chain(new,old,data)
    candidate,ancestor = output/'candidate',output/'predecessor'
    fresh(runner,candidate,data['implementation_sha'])
    fresh(runner,ancestor,PREDECESSOR)
    def metadata(ref):
        return dict(sha=ref,parents=[{'sha':p} for p in runner.git(candidate,'show','-s','--format=%P',ref).decode().split()],
                    tree={'sha':runner.git(candidate,'rev-parse',ref+'^{tree}').decode().strip()})
    chain(metadata(data['implementation_sha']),metadata(PREDECESSOR),data)
    # Reproduce original bytes/metadata proof only at its original commit. Do not
    # pretend that fixed v3's old tree/anchor approves a different implementation.
    publication.checked_owner_module(controls)
    runner.run('original-published-gate',[sys.executable,'-I','-B',controls/'scripts/v02_publication_gate.py',
        'published','--owner-revision',CONTROL,'--root',ancestor,'--ref',PREDECESSOR,'--output',output/'original-gate'],controls,timeout=600)
    a,b = tree(runner,candidate,PREDECESSOR),tree(runner,candidate,data['implementation_sha'])
    changed = {p for p in set(a)|set(b) if a.get(p)!=b.get(p)}
    require(changed=={r['path'] for r in data['changes']},'EXACT_CHANGED_PATH_SET')
    # Original40 exceptions,73 raw records, verifier/policy/manifest/attributes
    # remain immutable even if a proposed reviewed record tries to include them.
    owner = controls/'specs/migration/r03-v1/v02-publication'
    pins_raw = (owner/'approved-pins.json').read_bytes()
    require(sha(pins_raw)==PINS_SHA,'ORIGINAL_PINS_DIGEST')
    pins = decode(pins_raw)
    with zipfile.ZipFile(owner/'trusted-controls.zip') as z:
        policy_raw = z.read('exception-policy.json')
    require(sha(policy_raw)==pins['controls']['exception-policy.json']['sha256'],'ORIGINAL_POLICY_DIGEST')
    policy = decode(policy_raw)
    with zipfile.ZipFile(owner/'trusted-controls.zip') as z:
        bindings_raw = z.read('owner-handoff-bindings.json')
    require(sha(bindings_raw)==pins['controls']['owner-handoff-bindings.json']['sha256'],'ORIGINAL_BINDINGS_DIGEST')
    exclusions = decode(bindings_raw)['exception_paths']
    require(len(exclusions)==len(set(exclusions))==40 and len(policy['preserve_raw_bytes'])==73,'ORIGINAL_40_73_POLICY')
    protected = {r['path'] for r in policy['preserve_raw_bytes']}|{r['candidate_path'] for r in pins['controls'].values()}
    require(not changed.intersection(protected),'HISTORICAL_RAW_OR_CONTROL_MUTATION')
    same_delta({p:blob(runner,candidate,a.get(p)) for p in changed},
               {p:blob(runner,candidate,b.get(p)) for p in changed},data['changes'])
    patch = runner.git(candidate,'diff','--binary','--full-index','--no-renames','--no-ext-diff','--no-textconv',
                       '--src-prefix=a/','--dst-prefix=b/',PREDECESSOR,data['implementation_sha'])
    require(sha(patch)==data['patch_sha256'],'INDEPENDENT_REVIEWED_PATCH_DIGEST')
    for row in data['changes']:
        p = candidate/row['path']
        require(p.is_file() and not p.is_symlink() and not stat.S_IMODE(p.stat().st_mode)&0o111
                and sha(p.read_bytes())==row['after']['sha256'],'ACTUAL_WORKING_BYTES_MODE')
        attrs = runner.git(candidate,'check-attr','--all','-z','--stdin',data=(row['path']+'\0').encode())
        cached = runner.git(candidate,'check-attr','--cached','--all','-z','--stdin',data=(row['path']+'\0').encode())
        require(sha(attrs)==sha(cached)==row['attributes_sha256'],'REVIEWED_EFFECTIVE_ATTRIBUTES')
    for cr in (False,True):
        prefix = [runner.git_exe]+(['-c','core.whitespace=cr-at-eol'] if cr else [])
        runner.run('delta-whitespace-'+str(cr),prefix+['diff','--no-ext-diff','--no-textconv','--check',PREDECESSOR,data['implementation_sha']],candidate)
        for scoped in (False,True):
            args = prefix+['diff','--no-ext-diff','--no-textconv','--check',BASE,data['implementation_sha']]
            if scoped:
                args += ['--','.',*[':(exclude,literal)'+p for p in exclusions]]
            result = runner.run('full-whitespace-'+str(cr)+'-'+str(scoped),args,candidate,expected=0 if scoped else 2)
            expected = sha(b'') if scoped else ('5837278beb0d2ef638db564512c6913f9ae02346d204ba7b75c059aaef373f63' if cr else 'c1b69b199ac5cd41c665d656a72587d36ff0d13dc04a82c0a4c3d75086da20fb')
            require(not result.stderr and sha(result.stdout)==expected,'ORIGINAL_WHITESPACE_STREAM_CHANGED')
    require(not runner.git(candidate,'status','--porcelain'),'ACTUAL_CANDIDATE_CLEAN')
    require(runner.git(candidate,'rev-parse','HEAD').decode().strip()==data['implementation_sha']
            and runner.git(candidate,'write-tree').decode().strip()==data['tree_sha'],'ACTUAL_HEAD_AND_INDEX_TREE')
    after = publication.fetch_json('pulls/53',output,'pr-after')
    publication.validate_pr(after,dict(pr_number=53,implementation_sha=data['implementation_sha']))
    record = dict(result='PASS_SUCCESSOR_CHAIN_AND_REVIEWED_DELTA',implementation_sha=data['implementation_sha'],
        actual_checkout_sha=metadata(data['implementation_sha'])['sha'],actual_tree=metadata(data['implementation_sha'])['tree']['sha'],
        direct_parent=PREDECESSOR,accepted_base=BASE,original_control_revision=CONTROL,original_anchor_sha256=ANCHOR,
        reviewed_scope_sha256=digest,r03_control_revision=owner_revision,workflow_sha=os.environ.get('GITHUB_WORKFLOW_SHA'),
        pr_head_before=pr['head']['sha'],pr_head_after=after['head']['sha'],v02_task_approval=False,
        successor_task_suites='REQUIRED_SEPARATE_CURRENT_SHA_RUN',r03_status='INCOMPLETE')
    save(output/'result.json',record)
    return record


if __name__=='__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scope',type=Path,required=True)
    p.add_argument('--scope-sha256',required=True)
    p.add_argument('--owner-revision',required=True)
    p.add_argument('--controls',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args();out=args.output.resolve()
    require(not out.exists() and not out.is_relative_to(args.controls.resolve()) and not out.is_relative_to(ROOT),'NEW_EXTERNAL_OUTPUT_REQUIRED')
    out.mkdir(parents=True)
    try:
        print(json.dumps(execute(args.scope.resolve(),args.scope_sha256,args.owner_revision,args.controls.resolve(),out),indent=2))
    except Exception as error:
        save(out/'failure.json',dict(result='FAIL_OR_NOT_READY',error=str(error),r03_status='INCOMPLETE'))
        raise
    finally:
        save(out/'evidence-manifest.json',[dict(path=f.relative_to(out).as_posix(),size=f.stat().st_size,sha256=sha(f.read_bytes()))
            for f in out.rglob('*') if f.is_file() and not {'candidate','predecessor'}.intersection(f.relative_to(out).parts)])
