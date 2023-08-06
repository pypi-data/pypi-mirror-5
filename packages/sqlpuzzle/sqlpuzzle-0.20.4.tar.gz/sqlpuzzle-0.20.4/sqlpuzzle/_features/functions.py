# -*- coding: utf-8 -*-
#
# sqlpuzzle
# Michal Horejsek <horejsekmichal@gmail.com>
# https://github.com/horejsek/python-sqlpuzzle
#

import re

import sqlpuzzle._libs.object
import sqlpuzzle._libs.sqlValue

import sqlpuzzle._features.orderBy



class Function(sqlpuzzle._libs.object.Object):
    _functionName = None

    def __init__(self, expr):
        self._expr = sqlpuzzle._libs.sqlValue.SqlReference(expr)

    def __str__(self):
        if not self._functionName:
            return '<Function>'
        return '%s(%s)' % (
            self._functionName,
            self._expr,
        )

    @property
    def _expr(self):
        return self.__expr

    @_expr.setter
    def _expr(self, expr):
        self.__expr = expr



class FunctionWithDistinct(Function):
    def __init__(self, expr, distinct=False):
        super(FunctionWithDistinct, self).__init__(expr)
        self.distinct(distinct)

    def distinct(self, distinct=True):
        """Set DISTINCT."""
        self._distinct = bool(distinct)
        return self

    def __str__(self):
        if not self._functionName:
            return '<FunctionWithDistinct>'
        return '%s(%s%s)' % (
            self._functionName,
            self._strDistinct(),
            self._expr,
        )

    def _strDistinct(self):
        return 'DISTINCT ' if self._distinct else ''



class Avg(FunctionWithDistinct):
    _functionName = 'AVG'



class Count(FunctionWithDistinct):
    _functionName = 'COUNT'

    def __init__(self, expr=None, distinct=False):
        if not expr or expr == '*':
            self._expr = '*'
        else:
            if not isinstance(expr, (list, tuple)):
                expr = (expr,)
            self._expr = (sqlpuzzle._libs.sqlValue.SqlReference(e) for e in expr)

        self.distinct(distinct)

    @Function._expr.getter
    def _expr(self):
        expr = Function._expr.fget(self)
        return ', '.join(str(e) for e in expr)



class Max(FunctionWithDistinct):
    _functionName = 'MAX'



class Min(FunctionWithDistinct):
    _functionName = 'MIN'



class Sum(FunctionWithDistinct):
    _functionName = 'SUM'



class Concat(Function):
    _functionName = 'CONCAT'

    def __init__(self, *expr):
        self._columns = sqlpuzzle._features.columns.Columns().columns(*expr)
        if not self._columns.isSet():
            raise sqlpuzzle.exceptions.InvalidArgumentException('You must specify columns for %s.' % self._functionName)

    def __str__(self):
        return '%s(%s)' % (
            self._functionName,
            self._columns,
        )



class GroupConcat(Concat):
    _functionName = 'GROUP_CONCAT'

    def __init__(self, *expr):
        super(GroupConcat, self).__init__(*expr)
        self._orderBy = sqlpuzzle._features.orderBy.OrderBy()
        self._separator = None

    def __str__(self):
        return '%s(%s%s%s)' % (
            self._functionName,
            self._columns,
            self._strOrderBy(),
            self._strSeparator(),
        )

    def _strOrderBy(self):
        if self._orderBy.isSet():
            return ' %s' % self._orderBy
        return ''

    def _strSeparator(self):
        if self._separator:
            return ' SEPARATOR %s' % sqlpuzzle._libs.sqlValue.SqlValue(self._separator)
        return ''

    def orderBy(self, *args):
        self._orderBy.orderBy(*args)
        return self

    def separator(self, separator):
        self._separator = separator
        return self



class Convert(Function):
    _functionName = 'CONVERT'
    _allowedTypes = ('BINARY', 'CHAR', 'DATE', 'DATETIME', 'DECIMAL', 'SIGNED', 'TIME', 'UNSIGNED')

    def __init__(self, expr, type_=None):
        self._expr = sqlpuzzle._libs.sqlValue.SqlReference(expr)
        self._type = None
        if type_:
            self.to(type_)

    def __str__(self):
        return '%s(%s, %s)' % (
            self._functionName,
            self._expr,
            self._type,
        )

    def to(self, type_):
        type_ = str(type_).upper()
        self._checkType(type_)

        self._type = type_
        return self

    def _checkType(self, type_):
        type_ = type_.split('(')

        typeName = type_[0].strip()
        if typeName not in self._allowedTypes:
            raise sqlpuzzle.exceptions.InvalidArgumentException('You can convert value only into this types: %s' % repr(self._allowedTypes))

        if len(type_) > 2 or (len(type_) == 2 and type_[1][-1] != ')'):
            raise sqlpuzzle.exceptions.InvalidArgumentException('Invalid type in function %s.' % self._functionName)

        if len(type_) == 2 and not re.match('^[0-9]+(,[0-9]+)?\)$', type_[1]):
            raise sqlpuzzle.exceptions.InvalidArgumentException('In function %s you can set as param of type only the number.' % self._functionName)