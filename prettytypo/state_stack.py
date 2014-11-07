#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
.. module:: state_stack
   :platform: Independent
   :synopsis: Simple realization of state machine.

.. moduleauthor:: Evgeniy Bastrykov <vporoshok@gmail.com>

'''

from logging import getLogger


class StateDefault(object):
    '''Default State

    Use this class as mixin for you own states.

    Parameters:
        name (str, optional): init_name, default is None and will copied
            from real_name
        stack (:class:`.StateStack`, optional): stack that construct this
            instance, default is None and will created new StateStack

    Raises:
        TypeError: if container is not a collection or stack
            is not a :class:`.StateStack`

    Attributes:
        real_name (str): name with what it will be registered
            in :class:.`StateStack`
        init_name (str): name that has been given in constructor

        container (type): type of chunks and results. It must be a collection
        followers (list of str): list of eventual next states (by name)

        stack (:class:`.StateStack`): stack that construct this instance
        result (:attr:`.container`): result of all calling
        done (bool): is state done for pop from stack?

    '''

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
        self.result = self.container()
        if not hasattr(self.result, '__len__'):
            self.log.error('\'%s\' hasn\'t \'__len__\' method',
                           self.container)

            raise TypeError('State container must have \'__len__\' method')

    @classmethod
    def cond(cls, chunk, state):
        '''Condition to push this state

        Redefine this class method to provide auto push this state from other,
        that contains this in followers.

        Parameters:
            chunk (:attr:`.container`): current chunk to test
            state (State): current state

        Returns:
            bool: push this state to stack?

        '''
        # pylint: disable=unused-argument

        return False

    def __call__(self, chunk):
        '''Call wrapper

        This wrapper test chunk type and provide it to :meth:`.call`.
        If :meth:`.call` return True, store chunk to result.

        Parameters:
            chunk (:attr:`.container`): chunk of data

        Raises:
            TypeError: if chunk is not a :attr:`.container` type

        '''

        if not isinstance(chunk, self.container):
            self.log.error('chunk \'%s\' is not a instance of \'%s\'',
                           chunk, self.container)

            raise TypeError('Chunk must be instance of \'{0}\''
                            .format(self.container))

        if self.call(chunk):
            self.result += chunk

    def call(self, _):
        '''Main method for state

        Redefine this method to modify result.

        Parameters:
            chunk (:attr:`.container`): chunk of data

        Returns:
            bool: store this chunk to :attr:`.result`?

        '''

        return True

    def back(self, state):
        '''This method is called when children state has poped

        Redefine this method to modify and store result of child.

        Parameters:
            state (State): child state

        '''

        self.result += state.result

    def end(self):
        '''This method is called when :attr:`.done` is True

        Redefine this method to modify result before it will be passed
        to parent state.

        '''
        pass


class StateSet(object):
    '''Set of states types

    This is same as dict with test of values and default item.

    '''

    def __init__(self):
        self.log = getLogger('StateStack.States')
        self._states = {}
        self._states['default'] = StateDefault

    def __len__(self):
        '''Length of state classes'''

        return len(self._states)

    def __getitem__(self, name):
        '''Get state class by :attr:`.StateDefault.real_name`

        Parameters:
            name (str): :attr:`.StateDefault.real_name`

        Returns:
            StateClass: state class if there is or :class:`.StateDefault`

        '''

        if name not in self._states:
            self.log.warning('unknown state \'%s\'', name)
            self.log.info('use \'default\' state')
            name = 'default'

        return self._states[name]

    def __setitem__(self, name, value):
        '''Store state class by :attr:`.StateDefault.real_name`

        Parameters:
            name (str): :attr:`.StateDefault.real_name`
            value (StateClass): state class to store

        '''

        if not issubclass(value, StateDefault):

            raise TypeError('state must be inherit from StateDefault')

        if name in self._states:
            self.log.warning('state %s is already defined', name)
            self.log.info('overwriting state %s', name)

        self._states[name] = value


class StateStack(object):
    '''Stack of states

    This is a main state machine realization.

    '''

    def __init__(self):
        self.log = getLogger('StateStack')
        self._stack = []
        self._states = StateSet()

    def register(self, state_class):
        '''Register a state in machine

        Parameters:
            state_class (StateClass): state implementation class to register

        Raises:
            TypeError: if state_class is not subclass of :class:`.StateDefault`

        '''

        if not issubclass(state_class, StateDefault):

            raise TypeError('state must be inherit from StateDefault')

        self._states[state_class.real_name] = state_class

    def push(self, name):
        '''Push state in stack

        Get the state class by real_name from registered
        or :class:`.StateDefault` if there isn't. Initiate this state with
        :paramref:`.name` as :attr:`.StateDefault.init_name`
        and :paramref:`.self` as :attr:`.StateDefault.stack`.

        Parameters:
            name (str): :attr:`.StateDefault.real_name`

        '''

        self._stack.append(self._states[name](name, self))

    def __call__(self, chunk):
        '''Main method of machine

        At start test :meth:`.StateDefault.cond` for every state
        in :attr:`.StateDefault.followers` of :attr:`.current` and for first
        True this state is pushed to stack and then :paramref:`.chunk` provided
        to its :meth:`.StateDefault.__call__`. If no :meth:`.StateDefault.cond`
        has return True, :paramref:`.chunk` provided
        to :meth:`.StateDefault.__call__` of :attr:`.current`.

        After test is :attr:`.current` :attr:`.StateDefault.done`
        and :meth:`.pop` if True.

        Parameters:
            chunk (:attr:`.StateDefault.container`): chunk of data

        Raises:
            LookupError: if stack is empty

        '''

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
        '''Pop state from stack

        State is poped from stack. Then called :meth:`StateDefault.end` of it.
        Finally, if stack is not empty, the poped state provided
        to :meth:`.StateDefault.back` of stack head.

        '''

        if not len(self):
            self.log.warning('stack is empty')

            return None

        last_state = self._stack.pop()
        last_state.end()

        if self.current is not None:
            self.current.back(last_state)

    def __len__(self):
        '''Length of stack'''

        return len(self._stack)

    @property
    def current(self):
        '''The head of stack'''
        if not len(self):

            return None

        return self._stack[-1]
