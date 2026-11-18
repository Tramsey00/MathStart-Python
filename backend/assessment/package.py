"""Validate the whole pilot package before opening a write transaction."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
import re

from backend.infrastructure.json_input import decode_json
from backend.knowledge.graph import PILOT_CODES_DIGEST

from .templates import DIFFICULTY_BANDS, TEMPLATES

NUMBER_LINE = 'polozhitelnye-i-otriczatelnye-chisla-opredelenie-koordinatnoj-pryamoj'
ADDITION = 'algebraicheskaya-summa-raczionalnyh-chisel-s-raznymi-znakami'
MULTIPLICATION = 'umnozhenie-i-delenie-raczionalnyh-chisel'
EXPRESSIONS = 'uproshhenie-vyrazhenij-raskrytie-skobok'
EQUATIONS = 'reshenie-linejnyh-uravnenij'
TOPICS = {
    NUMBER_LINE: 'racionalnye-chisla',
    ADDITION: 'racionalnye-chisla',
    MULTIPLICATION: 'racionalnye-chisla',
    EXPRESSIONS: 'preobrazovanie-bukvennyh-vyrazhenij',
    EQUATIONS: 'preobrazovanie-bukvennyh-vyrazhenij',
}
PRIMARY_TOPICS = {
    'integer_number_line': NUMBER_LINE, 'negative_numbers': NUMBER_LINE,
    'sign_rules_add_sub': ADDITION, 'sign_rules_mul_div': MULTIPLICATION,
    'distributive_property': EXPRESSIONS, 'expand_parentheses': EXPRESSIONS,
    'combine_like_terms': EXPRESSIONS, 'equation_balance': EQUATIONS,
    'linear_one_step': EQUATIONS, 'linear_parentheses': EQUATIONS,
}


class BankError(ValueError):
    pass


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
                             allow_nan=False).encode()).hexdigest()


def text_value(value, max_length):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= max_length and '\0' not in value


def code_value(value):
    return isinstance(value, str) and re.fullmatch('[a-z][a-z0-9_]{0,63}', value)


def validation_data(row):
    template = TEMPLATES[row['schema']]
    return {
        'checker_type': template.checker,
        'checker_version': 1,
        'answer_key': row['answer'],
        'accepted_variants': row['variants'],
        'validation_spec': {
            'required_fields': [name for name, _ in template.fields],
            'step_type': template.step_type,
        },
        'canonical_solution': row['solution'],
    }


def validate_row(row):
    required = {'code', 'version', 'topic', 'schema', 'difficulty', 'statement', 'primary',
                'secondary', 'provenance', 'answer', 'variants', 'solution'}
    if (not isinstance(row, dict) or row.keys() != required or not code_value(row['code'])
            or type(row['version']) is not int or not 1 <= row['version'] < 2**31
            or not isinstance(row['topic'], str) or row['topic'] not in TOPICS
            or not isinstance(row['schema'], str) or row['schema'] not in TEMPLATES
            or type(row['difficulty']) is not int or row['difficulty'] not in DIFFICULTY_BANDS
            or not text_value(row['statement'], 2000) or not text_value(row['provenance'], 255)
            or not code_value(row['primary']) or not isinstance(row['secondary'], list)
            or not all(code_value(code) for code in row['secondary'])
            or len(set(row['secondary'])) != len(row['secondary']) or row['primary'] in row['secondary']
            or not isinstance(row['variants'], list) or not isinstance(row['solution'], list)
            or not row['solution'] or not all(text_value(step, 512) for step in row['solution'])):
        raise BankError('Invalid exercise fields or unknown input schema')
    if PRIMARY_TOPICS.get(row['primary']) != row['topic']:
        raise BankError('Primary skill belongs to a different pilot lesson')
    template = TEMPLATES[row['schema']]
    for answer in (row['answer'], *row['variants']):
        if template.mode == 'STRUCTURED_SOLUTION':
            fields = {name for name, _ in template.fields}
            if not isinstance(answer, dict) or answer.keys() != fields or not all(
                    text_value(value, 512) for value in answer.values()):
                raise BankError('Structured answer does not match its fields')
        elif not text_value(answer, 512):
            raise BankError('Invalid answer format')


def summarize(rows):
    modes = Counter()
    primary = Counter()
    levels = defaultdict(set)
    structures = set()
    topics = Counter()
    for row in rows:
        mode = TEMPLATES[row['schema']].mode
        modes[mode] += 1
        topics[row['topic']] += 1
        if mode == 'SELF_CHECK':
            continue
        primary[row['primary']] += 1
        levels[row['primary']].add(row['difficulty'])
        if mode == 'STRUCTURED_SOLUTION':
            structures.add(row['schema'])
    return {'modes': dict(modes), 'assessed': sum(primary.values()), 'primary': dict(primary),
            'levels': {code: sorted(values) for code, values in levels.items()},
            'structured_schemas': sorted(structures), 'topics': dict(topics)}


def read_package(path):
    max_bytes = 1024 * 1024
    with path.open('rb') as source:
        raw = source.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise BankError('Oversized bank package')
    data = decode_json(raw)
    if not isinstance(data, dict) or data.keys() != {'bank_version', 'exercises'} or (
            data['bank_version'] != 'pilot-v1' or not isinstance(data['exercises'], list)):
        raise BankError('Unknown or malformed pilot bank package')
    rows = data['exercises']
    return rows, validate_rows(rows), sha256(raw).hexdigest()


def validate_rows(rows):
    for row in rows:
        validate_row(row)
    if len({row['code'] for row in rows}) != len(rows):
        raise BankError('Duplicate exercise identity in bank')
    summary = summarize(rows)
    modes, primary = summary['modes'], summary['primary']
    codes = sorted(primary)
    if (summary['assessed'] != 40 or modes.get('SELF_CHECK', 0) < 3 or modes.get('STEP_BY_STEP', 0) < 12
            or modes.get('FINAL_ANSWER', 0) < 12 or len(summary['structured_schemas']) < 2
            or any(count != 4 for count in primary.values())
            or any(len(levels) < 2 for levels in summary['levels'].values())
            or digest(codes) != PILOT_CODES_DIGEST or set(summary['topics']) != set(TOPICS)):
        raise BankError('Pilot bank does not meet the coverage quotas')
    if any(code not in primary for row in rows for code in (row['primary'], *row['secondary'])):
        raise BankError('Bank references an unknown pilot skill')
    return summary
