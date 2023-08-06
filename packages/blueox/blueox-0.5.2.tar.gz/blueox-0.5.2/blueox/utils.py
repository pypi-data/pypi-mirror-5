# -*- coding: utf-8 -*-

"""
blueox.utils
~~~~~~~~

This module provides utility functions that are used within BlueOx

:copyright: (c) 2012 by Rhett Garber.
:license: ISC, see LICENSE for more details.

"""

class ParsedKey(object):
    def __init__(self, value):
        self.elems = []
        if '.' in value:
            for part in value.split('.'):
                try:
                    self.elems.append(int(part))
                except ValueError:
                    self.elems.append(part)
        else:
            self.elems.append(value)

    def __getitem__(self, key):
        return self.elems[key]

    def __getslice__(self, i, j, seq=None):
        usable_elems = self.elems[i:j:seq]
        if usable_elems:
            return ParsedKey('.'.join((str(v) for v in usable_elems)))
        else:
            return []

    def __len__(self):
        return len(self.elems)

    def __str__(self):
        return '.'.join((str(v) for v in self.elems))

def parse_key(key):
    return ParsedKey(key)

def get_deep(target, key, default=None):
    value = target
    for elem in parse_key(key):
        try:
            value = value[elem]
        except (KeyError, IndexError):
            return default

    return value

def set_deep(target, key, value):
    iter_value = target
    p_key = parse_key(key)
    for elem in p_key[:-1]:
        if isinstance(elem, int):
            raise ValueError(elem)

        iter_value = iter_value.setdefault(elem, {})

    iter_value[p_key[-1]] = value
