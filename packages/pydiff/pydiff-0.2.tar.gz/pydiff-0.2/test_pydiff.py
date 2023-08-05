#!/usr/bin/env python

"""Test suite for pydiff."""

from __future__ import unicode_literals

import os
import unittest

import pydiff


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


class UnitTests(unittest.TestCase):

    def test_disassemble(self):
        self.assertNotEqual(
            pydiff.disassemble('def main(): pass'),
            pydiff.disassemble('def main(): x = 1'))

    def test_disassemble_with_bad_syntax(self):
        with self.assertRaises(SyntaxError):
            pydiff.disassemble('def main():')

    def test_diff_bytecode(self):
        self.assertTrue(
            pydiff.diff_bytecode('x = 1', 'x=2'))

        self.assertFalse(
            pydiff.diff_bytecode('x = 1', 'x=1'))

    def test_diff_bytecode_should_ignore_docstrings(self):
        self.assertFalse(
            pydiff.diff_bytecode('def main(): """foo  """',
                                 'def main(): """foo"""'))

        self.assertFalse(
            pydiff.diff_bytecode('class Foo(object): """foo  """',
                                 'class Foo(object): """foo"""'))

    def test_diff_bytecode_of_files(self):
        self.assertTrue(
            pydiff.diff_bytecode_of_files(
                os.path.join(ROOT_DIR, 'setup.py'),
                os.path.join(ROOT_DIR, 'pydiff.py')))

        self.assertFalse(
            pydiff.diff_bytecode_of_files(
                os.path.join(ROOT_DIR, 'setup.py'),
                os.path.join(ROOT_DIR, 'setup.py')))


if __name__ == '__main__':
    unittest.main()

