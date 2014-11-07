#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger


class StateDefault(object):
    real_name = 'default'
    container = list
    followers = []

    def __init__(self, name=None, stack=None):
        self.log = getLogger('StateStack.{0}'.format(self.real_name))
        if name is None:
            name = self.real_name

        if stack is None:
            stack = StateStack()

        elif not isinstance(stack, StateStack):

            raise TypeError('{0} is not StateStack'.format(stack))

        self.stack = stack
        self.init_name = name
        self.done = False
        self._result = self.container()
        if not hasattr(self._result, '__len__'):
            self.log.error('\'%s\' hasn\'t \'__len__\' method',
                           self.container)

            raise TypeError('State container must have \'__len__\' method')

    @property
    def result(self):

        return self._result

    @classmethod
    def cond(cls, chunk, state):
        # pylint: disable=unused-argument

        return False

    def __call__(self, chunk):
        if not isinstance(chunk, self.container):
            self.log.error('chunk \'%s\' is not a instance of \'%s\'',
                           chunk, self.container)

            raise TypeError('Chunk must be instance of \'{0}\''
                            .format(self.container))

        if self.call(chunk):
            self._result += chunk

    def call(self, _):

        return True

    def back(self, state):
        self._result += state.result

    def end(self):
        pass


class States(object):
    def __init__(self):
        self.log = getLogger('StateStack.States')
        self._states = {}
        self._states['default'] = StateDefault

    def __len__(self):

        return len(self._states)

    def __getitem__(self, name):
        if name not in self._states:
            self.log.warning('unknown state \'%s\'', name)
            self.log.info('use \'default\' state')
            name = 'default'

        return self._states[name]

    def __setitem__(self, name, value):
        if not issubclass(value, StateDefault):

            raise TypeError('state must be inherit from StateDefault')

        if name in self._states:
            self.log.warning('state %s is already defined', name)
            self.log.info('overwriting state %s', name)

        self._states[name] = value


class StateStack(object):
    def __init__(self):
        self.log = getLogger('StateStack')
        self._stack = []
        self._states = States()

    def register(self, state_class):
        if not issubclass(state_class, StateDefault):

            raise TypeError('state must be inherit from StateDefault')

        self._states[state_class.real_name] = state_class

    def push(self, state_name):
        self._stack.append(self._states[state_name](state_name, self))

    def __call__(self, chunk):
        if not self._stack:
            self.log.error('stack is empty')

            raise LookupError('Stack stack is empty')

        for state_name in self.current.followers:
            state = self._states[state_name]
            if state.cond(chunk, self.current):
                self.push(state_name)

                break

        self.current(chunk)  # pylint: disable=not-callable

        if self.current.done:
            self.pop()

    def pop(self):
        if not len(self):
            self.log.warning('stack is empty')

            return None

        last_state = self._stack.pop()
        last_state.end()

        if self.current is not None:
            self.current.back(last_state)

        return last_state.result

    def __len__(self):

        return len(self._stack)

    @property
    def current(self):
        if not len(self):

            return None

        return self._stack[-1]
