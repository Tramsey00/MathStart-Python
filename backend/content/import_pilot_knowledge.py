"""Explicit operator command for the accepted Knowledge graph and Content mappings."""
import argparse
import json
from pathlib import Path
import sys

import sqlalchemy as sa

from backend.infrastructure.database import DatabaseConfig, create_engine
from backend.knowledge.graph import GraphError, graph_from_package
from backend.knowledge.repository import store_pilot_graph

from .topic_skills import (
    TopicSkillError, resolve_pilot_topics, store_pilot_mappings, validate_pilot_mappings,
)


FIXTURES = Path(__file__).resolve().parents[2] / 'specs' / 'knowledge' / 'fixtures'


def import_pilot(engine, skills, dependencies, mappings):
    graph = graph_from_package(skills, dependencies)
    pairs = validate_pilot_mappings(mappings)
    if engine.dialect.name != 'postgresql':
        raise ValueError('Pilot import requires PostgreSQL')

    # READ COMMITTED gives a waiter a fresh snapshot after the preceding import commits.
    with engine.connect().execution_options(isolation_level='READ COMMITTED') as connection, connection.begin():
        connection.execute(sa.text("SELECT pg_advisory_xact_lock(hashtextextended('mathstart.knowledge.pilot-v1', 0))"))
        pages = resolve_pilot_topics(connection, pairs)
        ids, graph_added = store_pilot_graph(connection, graph)
        mappings_added = store_pilot_mappings(connection, pairs, pages, ids)
    return {
        'graph_version': graph.graph_version,
        'status': 'IMPORTED' if graph_added or mappings_added else 'UNCHANGED',
        'skills': len(graph.skills),
        'dependencies': len(graph.dependencies),
        'topic_mappings': len(pairs),
        'mappings_added': mappings_added,
        'content_page_ids': pages,
    }


def read_fixture(name):
    def unique_object(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError('Duplicate key in pilot fixture')
        return result

    return json.loads((FIXTURES / name).read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', required=True, action='store_true', help='Import into the explicitly configured database')
    parser.parse_args(argv)
    engine = None
    try:
        package = [read_fixture(name) for name in ('pilot-skills-v1.json', 'pilot-dependencies-v1.json',
                                                   'pilot-topic-skills-v1.json')]
        engine = create_engine(DatabaseConfig.from_environment())
        receipt = import_pilot(engine, *package)
    except (GraphError, TopicSkillError) as error:
        print('PILOT_IMPORT_REFUSED: ' + str(error), file=sys.stderr)
        return 1
    except (sa.exc.SQLAlchemyError, OSError, ValueError) as error:
        print('PILOT_IMPORT_REFUSED_OR_UNCERTAIN: ' + type(error).__name__, file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
