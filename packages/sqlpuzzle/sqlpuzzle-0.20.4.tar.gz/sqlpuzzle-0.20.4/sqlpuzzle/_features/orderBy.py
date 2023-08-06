# -*- coding: utf-8 -*-
#
# sqlpuzzle
# Michal Horejsek <horejsekmichal@gmail.com>
# https://github.com/horejsek/python-sqlpuzzle
#

import sqlpuzzle._features.order


class OrderBy(sqlpuzzle._features.order.Orders):
    def __init__(self):
        """Initialization of OrderBy."""
        super(OrderBy, self).__init__()
        self._keywordOfFeature = 'ORDER BY'

    def orderBy(self, *args, **kwds):
        """Set ORDER BY."""
        self.order(*args, **kwds)
        return self
