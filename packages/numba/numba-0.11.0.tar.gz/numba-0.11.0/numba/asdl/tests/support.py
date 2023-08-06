# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import unittest

from numba.asdl import schema

def build_schema():
    '''Build a schema from Python.asdl
    '''
    return schema.load('Python.asdl')

class SchemaTestCase(unittest.TestCase):
    '''A base class for test cases that use the Python.asdl
    '''
    schema = build_schema()

    def capture_error(self):
        return self.assertRaises(schema.SchemaError)
