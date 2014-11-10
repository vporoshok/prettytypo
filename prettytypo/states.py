#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from prettytypo.state_stack import StateDefault
from prettytypo.config import config


class TextState(StateDefault):
    container = property(lambda _: '')


class Root(TextState):
    real_name = 'root'
    followers = [
        'command'
    ]


class Command(TextState):
    real_name = 'command'
    followers = [
        'parameter'
    ]

    @classmethod
    def cond(cls, chunk, _):

        return chunk == '\\'

    def init(self):
        self.key = ''

    def call(self, chunk):
        if not self.key and chunk == '\\':

            return True

        if config.match('command', chunk):
            self.key += chunk

            return True

        # TODO: Symbol and equation test

        self.done = True

        return True

    def back(self, state):
        self.result += state.result
        if self.key == 'begin' and state.key == '{':
            self.stack.pop()
            self.stack.push('environment', state.result)

        elif self.key == 'end' and state.key == '{':
            self.stack.pop()


class Parameter(TextState):
    real_name = 'parameter'
    followers = [
        'command'
    ]

    _brackets = {
        '{': '}',
        '[': ']'
    }

    @classmethod
    def cond(cls, chunk, state):
        if not state.key:

            return False

        return chunk in cls._brackets

    def call(self, chunk):
        if self.key is None:
            self.key = chunk

        if chunk == self._brackets[self.key]:
            self.done = True

        return True


class Environment(TextState):
    real_name = 'environment'
    followers = [
        'command'
    ]

    def init(self):
        if self.key == '{document}':
            self.stack.pop()
            self.stack.push('document')

        if config.match('ignored_env', self.key):
            self.stack.pop()

    def back(self, state):
        self.result += state.result
        if state.key == 'end'\
           and state.result.endswith('%s' % self.key):
            self.stack.pop()


class Document(TextState):
    real_name = 'document'
    followers = [
        'command'
    ]

    def init(self):
        self._newline = 0

    def call(self, chunk):
        if self._newline == 1 and chunk != '\n':
            self.result = self.result[:-1] + ' '
            self._newline = False

            return True

        if chunk == '\n':
            self._newline += 1

        else:
            self._newline = 0

        return True

    def back(self, state):
        self.result += state.result
        if self.result[-1] == '\n':
            self._newline += 1

        if state.key == 'end'\
           and state.result.endswith('{document}'):
            self.stack.pop()

STATES = [
    TextState,
    Root,
    Command,
    Parameter,
    Environment,
    Document
]
