"""Independent Django-only JSON oracle, run in the separate legacy interpreter."""
import json
import sys


def main():
    from unittest.mock import patch
    from django.conf import settings
    from django.core import signing
    from django.utils.text import smart_split, unescape_string_literal
    data = json.load(sys.stdin)
    settings.configure(SECRET_KEY=data.get('key', 'synthetic-search-only'), SECRET_KEY_FALLBACKS=[])
    if data['operation'] == 'signer':
        with patch('django.core.signing.time.time', return_value=data['clock']):
            token = signing.dumps(data['payload'], key=data['key'], salt=data['salt'], compress=data['compress'])
        result = {'token': token, 'decoded_target': signing.loads(data['target_token'], key=data['key'], salt=data['salt'])}
    elif data['operation'] == 'search':
        result = [[unescape_string_literal(word) if word[0] in {'"', "'"} and word[0] == word[-1] else word
                   for word in smart_split(query)] for query in data['queries']]
    else:
        raise ValueError('Unknown oracle operation')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
