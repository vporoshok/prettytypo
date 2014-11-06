#!/usr/bin/env python
# -*- coding: utf-8 -*-

from logging import getLogger


class ClassProperty(object):
    def __init__(self, function):
        self.function = function

    def __get__(self, _, owner):

        return self.function(owner)


class StateStack(object):
    def __init__(self):
        self.log = getLogger('StateStack')
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

    def __call__(self, chunk):
        if not self._stack:
            self.log.error('stack is empty')

            raise LookupError('Stack stack is empty')

        return self.current.call(chunk)

    def pop(self):
        if not len(self):
            self.log.warning('stack is empty')

            return None

        last_state = self._stack.pop()
        last_state.end()
        self.log.info('state \'%s\' has finished', last_state.name)
        self.log.info('result: \'\'\'%s\'\'\'', last_state.result)

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


class StateMixin(object):
    _name = 'default'
    _container = list

    def __init__(self, stack):
        self.log = getLogger('StateStack.{0}'.format(self._name))
        if not isinstance(stack, StateStack):

            raise TypeError('{0} is not StateStack'.format(stack))

        self.stack = stack
        self._result = self._container()
        if not hasattr(self._result, '__len__'):
            self.log.error('\'%s\' hasn\'t \'__len__\' method',
                           self._container)

            raise TypeError('State container must have \'__len__\' method')

    @ClassProperty
    def name(self):

        return self._name

    @property
    def result(self):

        return self._result

    def call(self, chunk):
        if not isinstance(chunk, self._container):
            self.log.error('chunk \'%s\' is not a instance of \'%s\'',
                           chunk, self._container)

            raise TypeError('Chunk must be instance of \'{0}\''
                            .format(self._container))

        self._result += chunk

        return None

    def back(self, state):
        self._result += state.result

    def end(self):
        pass
