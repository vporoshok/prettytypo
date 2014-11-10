#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from prettytypo.default import config as default


RegexObject = type(re.compile(''))


class Config(object):
    _instance = None

    def __init__(self):
        self._data = default

    def update(self, data):
        self._data.update(data)

    def match(self, name, value):
        if name not in self._data:

            raise KeyError('unknown key')

        if isinstance(self._data[name], RegexObject):

            return self._data[name].match(value)

        return value in self._data[name]


config = Config()

__all__ = ['config']
