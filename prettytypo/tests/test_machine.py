#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from prettytypo.machine import Machine, StateMixin


class TestMachine(TestCase):
    def test_init(self):
        machine = Machine()

        self.assertIsInstance(machine, Machine)
        self.assertEqual(len(machine), 0)

    def test_register_fail(self):
        machine = Machine()
        with self.assertRaises(TypeError):
            machine.register(list)

    def test_register(self):
        class TestState(StateMixin):
            _name = 'test'

        machine = Machine()
        machine.register(TestState)
        machine.push('test')

        self.assertEqual(machine.current.name, 'test')

    def test_push(self):
        machine = Machine()
        machine.push('state_name')

        self.assertEqual(len(machine), 1)
        self.assertEqual(machine.current.name, 'default')

    def test_call_fail(self):
        machine = Machine()
        with self.assertRaises(LookupError):
            machine(0)

    def test_call(self):
        machine = Machine()
        machine.push('state_name')
        res = machine([0])

        self.assertIsNone(res)
        self.assertListEqual(machine.current.result, [0])

    def test_pop(self):
        machine = Machine()
        machine.push('state_name')
        machine([0])
        res = machine.pop()

        self.assertListEqual(res, [0])
