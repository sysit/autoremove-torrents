#-*- coding:utf-8 -*-
from enum import Enum

Comparer = Enum('Comparer', ('LT', 'GT', 'EQ'))

class Condition(object):
    def __init__(self):
        # Results
        self.remain = set()
        self.remove = set()
    
    def compare(self, a, b, comp):
        return (comp == Comparer.LT and a < b) \
            or (comp == Comparer.GT and a > b) \
            or (comp == Comparer.EQ and a == b)

def require_settings(settings, keys):
    # Raise a clear error when required condition settings are missing,
    # instead of a bare KeyError deep in a condition class.
    missing = [key for key in keys if key not in settings]
    if missing:
        raise ValueError(
            'Missing required setting(s) %s. '
            'The condition needs these keys: %s.' %
            (', '.join("'%s'" % key for key in missing),
             ', '.join(keys))
        )