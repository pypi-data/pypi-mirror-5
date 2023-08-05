from kaiso.types import Entity, Relationship
from kaiso.queries import get_start_clause
from kaiso.attributes import String


class IndexableThing(Entity):
    indexable_attr = String(unique=True)


class TwoUniquesThing(IndexableThing):
    also_unique = String(unique=True)


class Connects(Relationship):
    indexable_attr = String(unique=True)


def test_get_start_clause_for_type():
    clause = get_start_clause(IndexableThing, "foo")
    assert clause == 'foo=node:persistablemeta(id="IndexableThing")'


def test_get_start_clause_for_instance():
    obj = IndexableThing(indexable_attr="bar")

    clause = get_start_clause(obj, "foo")
    assert clause == 'foo=node:indexablething(indexable_attr="bar")'


def test_get_start_clause_mutiple_uniques():
    obj = TwoUniquesThing(
        indexable_attr="bar",
        also_unique="baz"
    )

    clause = get_start_clause(obj, "foo")
    assert (clause == 'foo=node:indexablething(indexable_attr="bar")' or
            clause == 'foo=node:indexablething(also_unique="baz")')


def test_get_start_clause_for_relationship_type():
    clause = get_start_clause(Connects, "foo")
    assert clause == 'foo=node:persistablemeta(id="Connects")'


def test_get_start_clause_for_relationship_instance():
    a = IndexableThing()
    b = IndexableThing()

    obj = Connects(start=a, end=b, indexable_attr="bar")

    clause = get_start_clause(obj, "foo")
    assert clause == 'foo=rel:connects(indexable_attr="bar")'
