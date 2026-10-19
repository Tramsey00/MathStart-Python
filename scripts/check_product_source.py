from pathlib import Path
import json,re,hashlib,subprocess,collections,sys,argparse
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.historical_sources import retired_bytes, retired_json
started=datetime.now(timezone.utc).isoformat()
parser=argparse.ArgumentParser(description='Read-only product source reconciliation; optional new report under var/')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
if args.output and (args.output.exists() or not args.output.resolve().is_relative_to(Path('var').resolve())):parser.error('New owned report under var/ required')
checks=[]
def check(ok,label):
    assert ok,label
    checks.append(label)
def edges(body):
    out=[]
    for kind,nxt in [('HARD','CONTRACT'),('CONTRACT','HANDOFF'),('HANDOFF','INTEGRATION'),('INTEGRATION','Что можно делать параллельно')]:
        m=re.search(kind+':(.*?)'+nxt+':',body,re.S)
        assert m,kind
        tokens=re.findall(r'MS[67]-?[RVI]\d{2}[AB]?|(?<![\w-])R0[23](?!\w)',m[1])
        out.extend((kind,re.sub(r'^(MS[67])(?=[RVI])',r'\1-',x)) for x in tokens)
    return set(out)
s=Path('docs/specifications/technical-spec-v7.2-draft.md').read_text(encoding='utf-8')
r=json.loads(Path('specs/product/task-dispositions-v7.2.json').read_text(encoding='utf-8'))
a=retired_json('docs/acceptance/migration-execution/product-source-audit.json')
old=json.loads(subprocess.check_output(['git','show','953fe979742784a196efab203ab987c0cfefd3b3:docs/acceptance/migration-execution/product-task-disposition-draft.json']).decode('utf-8'))
check(hashlib.sha256(retired_bytes(r['source_pdf'])).hexdigest()==r['source_pdf_sha256']==a['source_pdf_sha256'],'original PDF byte hash unchanged')
check([int(x) for x in re.findall(r'(?m)^## (\d+)\.',s)]==list(range(1,33)),'all32 chapters exactly once in order')
heads=list(re.finditer(r'(?m)^### (MS7-[RVI]\d{2}[AB]?)\s*·[^\n]*',s))
check(len(heads)==52 and {m[1] for m in heads}=={x['id'] for x in r['rows']},'all52 source card IDs exactly once')
check(len({x['id'] for x in r['rows']})==52,'registry IDs unique')
for i,m in enumerate(heads):
    row=next(x for x in r['rows'] if x['id']==m[1])
    body=s[m.end():heads[i+1].start() if i+1<len(heads) else s.index('## 25.')]
    expected={(d['kind'],d['id']) for d in row['dependencies']}
    check(edges(body)==edges(row['source_card_text'])==expected,m[1]+' typed edges equal source/registry/adapted card')
    check(hashlib.sha256(row['source_card_text'].encode()).hexdigest()==row['source_card_text_sha256'],m[1]+' complete source excerpt digest')
    previous=next(x for x in old['rows'] if x['id']==m[1])
    check(all(row.get(k)==previous.get(k) for k in ['original_result','original_result_source','current_acceptance_reconciliation','dependencies','current_status','platform_disposition']),m[1]+' historical result/acceptance/dependencies/disposition retained')
check(sum(len(row['dependencies']) for row in r['rows'])==115,'all115 typed source edges retained')
check(dict(collections.Counter(d['kind'] for row in r['rows'] for d in row['dependencies']))==r['source_dependency_audit']['by_kind'],'dependency kinds exact60/24/6/25')
check(sum(row['platform_disposition']=='PLANNED_EQUIVALENT' and row['current_status']=='PLANNED' and not row['target_evidence'] for row in r['rows'])==47,'all47 future product equivalents remain planned without fabricated runtime evidence')
for fix in a['operator_repairs']:
    check(re.sub(r'[\s≤≥→#]','',fix['old'])==re.sub(r'[\s≤≥→#]','',fix['new']) and fix['new'] in s,'glyph placement only at original line'+str(fix['line']))
for p in ['docs/specifications/technical-spec-v7.2-draft.md','specs/product/task-dispositions-v7.2.json']:
    check(hashlib.sha256(Path(p).read_bytes()).hexdigest() in Path('docs/specifications/technical-spec-v7.2-provenance.md').read_text(encoding='utf-8'),p+' current provenance digest')
report={'status':'PASS_SCOPED_DOCUMENT_SOURCE_RECONCILIATION','assertions':len(checks),'case_ids':checks,'source_pdf_sha256':r['source_pdf_sha256'],'full_target':'NOT_RUN','formal_acceptance':'HUMAN_PENDING','started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'argv':[sys.executable,*sys.argv],'cwd':str(Path.cwd()),'python':sys.version,'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'exit_code':0,'previous_failure':{'assertion':'all32 chapters exactly once in order','reason':'Six additional PDF list fragments were incorrectly promoted to chapter headings by the old draft. Removed those headings, preserved all text/numerical values, then reran the source checks.'}}
if args.output:
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x',encoding='utf-8',newline='\n') as output:output.write(json.dumps(report,indent=2)+'\n')
print('PASS',len(checks),'source/document checks')
