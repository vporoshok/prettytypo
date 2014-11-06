#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger


class Machine(object):
    log = getLogger('StateMachine')

    def __init__(self):
        self._stack = []
        self._states = {
            'default': StateMixin
        }

    def register(self, state_class):
        if not issubclass(state_class, StateMixin):

            raise TypeError('{0} is not State'.format(state_class))

        self._states[state_class.name] = state_class

    def push(self, state_name):
        if state_name not in self._states:
            self.log.warning('unknown state \'%s\'', state_name)
            self.log.info('use \'default\' state')
            state_name = 'default'

        self.log.info('append \'%s\' state')
        self._stack.append(self._states[state_name](self))

    def __call__(self, *args, **kwargs):
        if not self._stack:
            self.log.error('stack is empty')

            raise LookupError('Machine stack is empty')

        return self._stack[-1].call(*args, **kwargs)

    def pop(self):
        if not self._stack:
            self.log.warning('stack is empty')

            return None

        last_state = self._stack.pop()
        last_state.end()
        self.log.info('state \'%s\' has finished', last_state.name)
        self.log.info('result: \'\'\'%s\'\'\'', last_state.result)

        self._stack[-1].back(last_state)

        return last_state.result


class StateMixin(object):
    name = 'default'

    def __init__(self, machine):
        if not isinstance(machine, Machine):

            raise TypeError('{0} is not Machine'.format(machine))

        self.machine = machine
        self._result = ''

    @property
    def result(self):

        return self._result

    def call(self, char):
        self._result += char

    def back(self, state):
        self._result += state.result

    def end(self):
        pass
