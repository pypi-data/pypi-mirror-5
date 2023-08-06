# -*- coding: utf-8 -*-
#
# sqlpuzzle
# Michal Horejsek <horejsekmichal@gmail.com>
# https://github.com/horejsek/python-sqlpuzzle
#

import sqlpuzzle._features



class CustomSql(sqlpuzzle._features.Feature):
    def __init__(self, string=''):
        """Initialization of CustomSql"""
        self._customSqlString = string

    def __str__(self):
        """Print custom SQL"""
        return self._customSqlString
