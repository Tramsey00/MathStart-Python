"""Persist and read the verified pilot graph without depending on Content."""
from uuid import uuid4

import sqlalchemy as sa

from .graph import DependencyRead, GraphError, PILOT_VERSION, SkillRead, validate_pilot
from .models import skill, skill_dependency


def read_pilot_graph(database):
    """Read the installed graph as immutable DTOs, or None before explicit import."""
    parent = skill.alias('prerequisite')
    child = skill.alias('dependent')
    edges = sa.select(parent.c.code, child.c.code, skill_dependency.c.weight).select_from(
        skill_dependency.join(parent, skill_dependency.c.prerequisite_id == parent.c.id)
        .join(child, skill_dependency.c.dependent_id == child.c.id)
    ).where(sa.or_(parent.c.graph_version == PILOT_VERSION, child.c.graph_version == PILOT_VERSION))
    # One statement gives skills and edges the same snapshot even during first import.
    nodes = sa.select(skill.c.code, skill.c.name, skill.c.active).where(skill.c.graph_version == PILOT_VERSION)
    rows = database.execute(sa.union_all(
        nodes.with_only_columns(sa.literal('skill'), skill.c.code, skill.c.name, skill.c.active,
                                sa.cast(sa.null(), sa.Numeric())),
        edges.with_only_columns(sa.literal('edge'), parent.c.code, child.c.code,
                                sa.cast(sa.null(), sa.Boolean()), skill_dependency.c.weight),
    )).all()
    if not rows:
        return None
    return validate_pilot(
        (SkillRead(code, name, active) for kind, code, name, active, _ in rows if kind == 'skill'),
        (DependencyRead(source, target, weight) for kind, source, target, _, weight in rows if kind == 'edge'),
    )


def store_pilot_graph(connection, graph):
    """Called inside the operator's serialized import transaction."""
    existing = read_pilot_graph(connection)
    if existing is not None and existing != graph:
        raise GraphError('Installed pilot graph differs from the import package')
    if existing is None:
        ids = {node.code: uuid4() for node in graph.skills}
        connection.execute(skill.insert(), [
            dict(id=ids[node.code], code=node.code, name=node.name, active=node.active, graph_version=PILOT_VERSION)
            for node in graph.skills
        ])
        connection.execute(skill_dependency.insert(), [
            dict(id=uuid4(), prerequisite_id=ids[edge.prerequisite], dependent_id=ids[edge.dependent], weight=edge.weight)
            for edge in graph.dependencies
        ])
        return ids, True
    return dict(connection.execute(sa.select(skill.c.code, skill.c.id).where(
        skill.c.graph_version == PILOT_VERSION)).tuples().all()), False
