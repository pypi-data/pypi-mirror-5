# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils import tree
from django.db.models.sql.datastructures import MultiJoin

# Python3 compatibility
import sys

if sys.version_info[0] == 3:
    text = str
else:
    text = unicode


class CommonBaseTree(tree.Node):
    """
    Encapsulates filters as objects that can then be combined logically (using
    & and |).
    """
    # Connection types
    AND = 'AND'
    OR = 'OR'
    default = AND
    query = None

    def __init__(self, *args, **kwargs):
        super(CommonBaseTree, self).__init__(children=list(args) + list(kwargs.items()))

    def _combine(self, other, conn):
        if not isinstance(other, (BaseTree)):
            raise TypeError(other)
        obj = type(self)()
        obj.add(self, conn)
        obj.add(other, conn)
        return obj

    def __or__(self, other):
        return self._combine(other, self.OR)

    def __and__(self, other):
        return self._combine(other, self.AND)

    def __invert__(self):
        obj = type(self)()
        obj.add(self, self.AND)
        obj.negate()
        return obj

    def set_query(self, query):
        self.query = query
        return self


class RawSQL(object):
    def __init__(self, items, connector, query=None):
        self.items = items
        self.connector = connector
        self.query = query

    if sys.version_info[0] == 3:
        def __str__(self):
            connector = " %s " % (self.connector)
            return connector.join(self.items)
    else:
        def __str__(self):
            connector = b" %s " % (self.connector)
            return connector.join(self.items)

        def __unicode__(self):
            return self.__str__().decode('utf-8')

    def to_str(self, closure=False):
        if closure:
            return "(%s)" % text(self)
        return text(self)


class OperatorTree(CommonBaseTree):
    """
    Base operator node class.
    """
    def as_sql(self, qn, queryset):
        items, params = [], []

        for child in self.children:
            _sql, _params = child.as_sql(qn, queryset)

            if isinstance(_sql, RawSQL):
                _sql = _sql.to_str(True)

            items.extend([_sql])
            params.extend(_params)

        sql_obj = RawSQL(items, self._connector, queryset)
        return sql_obj, params


class AND(OperatorTree):
    _connector = "AND"


class OR(OperatorTree):
    _connector = "OR"
