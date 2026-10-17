"""Verified immutable H-BUILD-INPUTS -> build-only React view models.

The frozen numeric wire JSON is never rewritten. Internal ID labels use decimal
text after Python validates exact int64 numbers, avoiding JavaScript rounding.
"""
import argparse
import json
from pathlib import Path
from uuid import UUID
from frontend.build_input import verified_release
from frontend.rendering import catalogue_html


def view_model(value, key=''):
    if type(value) is int and (key == 'id' or key.endswith('_id')):
        return str(value)
    if isinstance(value, dict):
        return {k:view_model(v, k) for k,v in value.items()}
    if isinstance(value, list):
        return [view_model(v) for v in value]
    return value


def prepare(input_root, release_id, manifest_digest, origin, output, receipt_digest):
    release = verified_release(input_root, release_id, manifest_digest, receipt_digest)
    data = {}
    for entry in release.index['pages']:
        page = release.pages[entry['id']]
        context = release.renderer_context(page, {})
        data[entry['url']] = view_model({'page':page, 'context':context,
            'catalogue_html':catalogue_html(context) if page['slug'] == 'karta-sajta' else None,
            'canonical_url':origin.rstrip('/') + page['seo']['canonical_path']})
    for alias in release.index['aliases']:
        data[alias['url']] = data[release.pages[alias['page_id']]['seo']['canonical_path']]
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'version':'react-public-view-v1','release_id':release_id,
        'manifest_digest':manifest_digest,'routes':data}, ensure_ascii=False), encoding='utf-8')
    return len(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('input-root','release-id','manifest-digest','origin','output','receipt-digest'):
        parser.add_argument('--' + name, required=True)
    print('Prepared public routes:', prepare(**vars(parser.parse_args())))
