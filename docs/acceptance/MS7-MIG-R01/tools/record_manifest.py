"""Hash exact R01 Git blobs from staged INDEX or an explicit review commit.

Excludes its own output. Input source manifest is a separate frozen snapshot.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

INPUT = '8c11edadc8debc81432d1db1145feac504f09061'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ref', default='INDEX')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[4]
    def git(*argv):
        return subprocess.check_output(['git','-C',str(root),*argv])
    command = ['diff','--cached','--name-only',INPUT] if args.ref == 'INDEX' else ['diff','--name-only',INPUT,args.ref]
    paths = git(*command).decode('utf-8').splitlines()
    rows = []
    for name in paths:
        if name == 'docs/acceptance/MS7-MIG-R01/record-manifest.json':
            continue
        data = git('show',(':' if args.ref == 'INDEX' else args.ref + ':') + name)
        checkout = (root / name).read_bytes()
        rows.append({'path':name,'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                     'checkout_size':len(checkout),'checkout_sha256':hashlib.sha256(checkout).hexdigest()})
    result = {'input_commit':INPUT,'digest_semantics':'Exact R01 Git blob bytes; checkout hashes separate. Excludes this manifest itself. Candidate containing SHA is external snapshot PR/head evidence, avoiding circular self-pins.', 'files':rows}
    (root / 'docs/acceptance/MS7-MIG-R01/record-manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'records':len(rows),'git_blob_bytes':sum(x['size'] for x in rows)}))

if __name__ == '__main__':
    main()
