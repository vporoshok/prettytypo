#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase

from prettytypo.machine import Machine  # , StateMixin


class TestMachine(TestCase):
    def test_init(self):
        machine = Machine()

        self.assertIsInstance(machine, Machine)
