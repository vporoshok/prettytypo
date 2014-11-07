#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from prettytypo.state_stack import StateDefault, States, StateStack


class TestStateDefault(TestCase):
    def test_init(self):
        state = StateDefault()

        self.assertIsInstance(state, StateDefault)
        self.assertEqual(state.real_name, 'default')
        self.assertEqual(state.init_name, 'default')
        self.assertListEqual(state.result, [])

    def test_init_fail(self):
        with self.assertRaises(TypeError):
            StateDefault(stack=0)

    def test_bad_container(self):
        class BadState(StateDefault):
            real_name = 'bad'
            container = int

        with self.assertRaises(TypeError):
            BadState()

    def test_cond(self):

        self.assertFalse(StateDefault.cond(None, None))

    def test_exec(self):
        state = StateDefault()
        state([0])

        self.assertListEqual(state.result, [0])

    def test_exec_fail(self):
        state = StateDefault()
        with self.assertRaises(TypeError):
            state(0)

    def test_back(self):
        state1 = StateDefault()
        state2 = StateDefault()
        state2([0])
        state1.back(state2)

        self.assertListEqual(state1.result, [0])

    def test_end(self):
        StateDefault().end()


class TestStates(TestCase):
    def test_init(self):
        states = States()

        self.assertIsInstance(states, States)
        self.assertEqual(len(states), 1)

    def test_getitem(self):
        states = States()

        self.assertEqual(states['default'], StateDefault)
        self.assertEqual(states['test'], StateDefault)

    def test_setitem(self):
        class TestState(StateDefault):
            real_name = 'test'
        states = States()

        with self.assertRaises(TypeError):
            states['test'] = int

        states['default'] = TestState

        self.assertEqual(states['default'].real_name, 'test')


class TestMachine(TestCase):
    def test_init(self):
        stack = StateStack()

        self.assertIsInstance(stack, StateStack)
        self.assertEqual(len(stack), 0)

    def test_register(self):
        class TestState(StateDefault):
            real_name = 'test'

        stack = StateStack()
        stack.register(TestState)
        stack.push('test')

        self.assertEqual(stack.current.real_name, 'test')
        self.assertEqual(stack.current.init_name, 'test')

    def test_register_fail(self):
        stack = StateStack()
        with self.assertRaises(TypeError):
            stack.register(list)

    def test_push(self):
        stack = StateStack()
        stack.push('state_name')

        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.current.real_name, 'default')
        self.assertEqual(stack.current.init_name, 'state_name')

    def test_call(self):
        stack = StateStack()
        stack.push('state_name')
        res = stack([0])

        self.assertIsNone(res)
        self.assertListEqual(stack.current.result, [0])

    def test_call_fail(self):
        stack = StateStack()
        with self.assertRaises(LookupError):
            stack(0)

    def test_pop(self):
        stack = StateStack()
        res1 = stack.pop()
        stack.push('state_name')
        stack.push('state_name')
        stack([0])
        res2 = stack.pop()

        self.assertIsNone(res1)
        self.assertListEqual(res2, [0])
        self.assertListEqual(stack.current.result, [0])

    def test_current(self):
        stack = StateStack()

        self.assertIsNone(stack.current)

    def test_chain(self):
        class FirstState(StateDefault):
            real_name = 'first'
            followers = ['second']

        class SecondState(StateDefault):
            real_name = 'second'

            @classmethod
            def cond(cls, chunk, _):

                return chunk[0] == 0

            def call(self, chunk):
                if chunk[0] == 1:
                    self.done = True

                return True

        stack = StateStack()
        stack.register(FirstState)
        stack.register(SecondState)
        stack.push('first')
        stack([1])
        self.assertEqual(stack.current.real_name, 'first')
        self.assertLessEqual(stack.current.result, [1])
        stack([0])
        self.assertEqual(stack.current.real_name, 'second')
        self.assertLessEqual(stack.current.result, [0])
        stack([1])
        self.assertEqual(stack.current.real_name, 'first')
        self.assertLessEqual(stack.current.result, [1, 0, 1])
