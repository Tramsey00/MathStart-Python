"""Pure R03 graph validation and traversal, shared by import and persisted reads."""
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from heapq import heapify, heappop, heappush
import json
import re


PILOT_VERSION = 'pilot-v1'
# Digests of the sorted codes and directed pairs in the accepted R03 fixtures.
PILOT_CODES_DIGEST = 'd7a339343bbe6bc8968e5630450f25d507a94cffa2876bcd42aa82fb537ab206'
PILOT_PAIRS_DIGEST = '49a2fb48f838c5b705073a76bb55f121850acd3b2698a01430680277501bdad9'


class GraphError(ValueError):
    pass


@dataclass(frozen=True)
class ExternalPrerequisite:
    code: str = 'basic_arithmetic'
    scope: str = 'pilot_entry'
    representation: str = 'outside_skill_dependency'


@dataclass(frozen=True, order=True)
class SkillRead:
    code: str
    name: str
    active: bool = True


@dataclass(frozen=True, order=True)
class DependencyRead:
    prerequisite: str
    dependent: str
    weight: Decimal


@dataclass(frozen=True)
class PilotGraphRead:
    skills: tuple[SkillRead, ...]
    dependencies: tuple[DependencyRead, ...]
    topological_order: tuple[str, ...]
    graph_version: str = PILOT_VERSION
    external_prerequisite: ExternalPrerequisite = ExternalPrerequisite()

    def ancestors(self, skill_code: str, max_depth: int = 2) -> tuple[tuple[str, int], ...]:
        if not any(node.code == skill_code for node in self.skills):
            raise GraphError('Unknown pilot skill')
        if type(max_depth) is not int or max_depth not in (0, 1, 2):
            raise GraphError('Pilot ancestor depth must be 0, 1, or 2')
        seen = {skill_code}
        frontier = {skill_code}
        result = []
        for depth in range(1, max_depth + 1):
            frontier = {edge.prerequisite for edge in self.dependencies if edge.dependent in frontier} - seen
            result.extend((code, depth) for code in sorted(frontier))
            seen.update(frontier)
        return tuple(result)


def validate_dag(codes, pairs) -> tuple[str, ...]:
    children = {}
    for code in codes:
        if not isinstance(code, str) or not re.fullmatch('[a-z][a-z0-9_]{0,63}', code):
            raise GraphError('Invalid skill code')
        if code in children:
            raise GraphError('Duplicate skill code')
        children[code] = set()
    incoming = dict.fromkeys(children, 0)
    for prerequisite, dependent in pairs:
        if prerequisite not in children or dependent not in children:
            raise GraphError('Dependency references an unknown skill')
        if prerequisite == dependent:
            raise GraphError('Self-dependency')
        if dependent in children[prerequisite]:
            raise GraphError('Duplicate dependency')
        children[prerequisite].add(dependent)
        incoming[dependent] += 1
    ready = [code for code, count in incoming.items() if count == 0]
    heapify(ready)
    order = []
    while ready:
        code = heappop(ready)
        order.append(code)
        for dependent in children[code]:
            incoming[dependent] -= 1
            if incoming[dependent] == 0:
                heappush(ready, dependent)
    if len(order) != len(children):
        raise GraphError('Cyclic dependencies')
    return tuple(order)


def validate_pilot(skills, dependencies) -> PilotGraphRead:
    skills, dependencies = tuple(skills), tuple(dependencies)
    codes = [node.code for node in skills]
    pairs = [(edge.prerequisite, edge.dependent) for edge in dependencies]
    order = validate_dag(codes, pairs)
    for values, count, expected in ((codes, 10, PILOT_CODES_DIGEST), (pairs, 13, PILOT_PAIRS_DIGEST)):
        digest = sha256(json.dumps(sorted(values), separators=(',', ':')).encode()).hexdigest()
        if len(values) != count or digest != expected:
            raise GraphError('Pilot skill codes or directed dependencies differ from R03')
    if any(edge.weight != 1 for edge in dependencies):
        raise GraphError('Pilot dependencies require weight 1')
    if any(not isinstance(node.name, str) or not node.name.strip() or len(node.name) > 160 for node in skills):
        raise GraphError('Invalid skill name')
    return PilotGraphRead(tuple(sorted(skills)), tuple(sorted(dependencies)), order)


def graph_from_package(skills, dependencies) -> PilotGraphRead:
    try:
        if skills['graph_version'] != PILOT_VERSION or dependencies['graph_version'] != PILOT_VERSION:
            raise GraphError('Unexpected pilot graph version')
        if skills['external_prerequisite'] != vars(ExternalPrerequisite()):
            raise GraphError('Invalid pilot entry prerequisite')
        nodes = tuple(SkillRead(row['code'], row['name']) for row in skills['skills'])
        edges = []
        for row in dependencies['edges']:
            weight = row['weight']
            if type(weight) not in (int, float, Decimal) or weight != 1:
                raise GraphError('Pilot dependencies require numeric weight 1')
            if not isinstance(row['prerequisite'], str) or not isinstance(row['dependent'], str):
                raise GraphError('Invalid dependency skill code')
            edges.append(DependencyRead(row['prerequisite'], row['dependent'], Decimal(weight)))
        return validate_pilot(nodes, edges)
    except (KeyError, TypeError) as error:
        raise GraphError('Malformed pilot graph package') from error
