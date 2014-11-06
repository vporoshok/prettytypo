#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from prettytypo.state_stack import StateStack, StateMixin


class TestMachine(TestCase):
    def test_init(self):
        stack = StateStack()

        self.assertIsInstance(stack, StateStack)
        self.assertEqual(len(stack), 0)

    def test_register(self):
        class TestState(StateMixin):
            _name = 'test'

        stack = StateStack()
        stack.register(TestState)
        stack.push('test')

        self.assertEqual(stack.current.name, 'test')

    def test_register_fail(self):
        stack = StateStack()
        with self.assertRaises(TypeError):
            stack.register(list)

    def test_push(self):
        stack = StateStack()
        stack.push('state_name')

        self.assertEqual(len(stack), 1)
        self.assertEqual(stack.current.name, 'default')

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


class TestStateMixin(TestCase):
    def test_init(self):
        stack = StateStack()
        state = StateMixin(stack)

        self.assertIsInstance(state, StateMixin)
        self.assertEqual(state.name, 'default')
        self.assertListEqual(state.result, [])

    def test_init_fail(self):
        with self.assertRaises(TypeError):
            StateMixin(0)

    def test_bad_container(self):
        class BadState(StateMixin):
            _name = 'bad'
            _container = int

        stack = StateStack()
        with self.assertRaises(TypeError):
            BadState(stack)

    def test_exec(self):
        stack = StateStack()
        state = StateMixin(stack)
        state.call([0])

        self.assertListEqual(state.result, [0])

    def test_exec_fail(self):
        stack = StateStack()
        state = StateMixin(stack)
        with self.assertRaises(TypeError):
            state.call(0)

    def test_back(self):
        stack = StateStack()
        state1 = StateMixin(stack)
        state2 = StateMixin(stack)
        state2.call([0])
        state1.back(state2)

        self.assertListEqual(state1.result, [0])
