"""Local artifact preview only; no DB activation or identity/API acceptance claim."""
import argparse
import json
import mimetypes
from pathlib import Path
from urllib.parse import quote
from fastapi import FastAPI, Request
from starlette.responses import Response
import uvicorn
from frontend.build_input import verified_release
from frontend.rendering import PublicRenderer
from backend.content.releases import inside


def create_preview(config):
    release = verified_release(config['input_root'], config['release_id'], config['manifest_digest'], config['receipt_digest'])
    renderer = PublicRenderer(config['output'],{config['release_id']:config['output_digest']})
    root = Path(config['output']).resolve()
    receipt = json.loads((root / 'output-manifest.json').read_text(encoding='utf-8'))
    exported = {row['url']: row for row in receipt['files'] if row['url']}
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    @app.get('/{path:path}')
    def document(request: Request, path: str):
        url = '/' + path
        if url.startswith(('/api/', '/_private/', '/__ui__/', '/_content/')):
            return Response(status_code=404)
        if url.startswith(('/account/', '/admin/')):
            return Response((root / '_private/shell.html').read_bytes(),media_type='text/html',headers={'Cache-Control':'no-store'})
        try:
            page = release.page_path(url)
        except Exception:
            page = None
        if page is not None:
            return Response(renderer(page, release.renderer_context(page, request.query_params), config['origin'] + page['seo']['canonical_path']),media_type='text/html')
        entry = exported.get(url)
        if entry:
            return Response(inside(root, entry['path']).read_bytes(),media_type=mimetypes.guess_type(url)[0] or 'application/octet-stream')
        if url.startswith('/assets/'):
            path = inside(root,url.lstrip('/'))
            if path.is_file():return Response(path.read_bytes(),media_type=mimetypes.guess_type(url)[0])
        redirect = release.redirect(url)
        if redirect:return Response(status_code=301 if redirect['is_permanent'] else 302,headers={'Location':quote(redirect['new_path'],safe='/%')})
        if not url.endswith('/') and any(entry['url'] == url+'/' for entry in release.index['pages']):
            return Response(status_code=301,headers={'Location':url+'/'})
        return Response((root / '404.html').read_bytes(),status_code=404,media_type='text/html')
    return app

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--port',type=int,default=8131)
    args=parser.parse_args();config=json.loads(Path(args.config).read_text(encoding='utf-8-sig'))
    uvicorn.run(create_preview(config),host='127.0.0.1',port=args.port,access_log=False)
