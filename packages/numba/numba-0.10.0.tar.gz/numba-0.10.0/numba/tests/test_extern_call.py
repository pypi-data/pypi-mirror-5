#! /usr/bin/env python
# ______________________________________________________________________
'''test_extern_call

Unit tests checking on Numba's code generation for Python/Numpy C-API calls.
'''
# ______________________________________________________________________

import sys
import unittest

from numba import *

import numpy
from numba.decorators import jit, autojit
from numba.testing import test_support

# ______________________________________________________________________

def call_zeros_like(arr):
    return numpy.zeros_like(arr)

# ______________________________________________________________________

def call_len(arr):
    return len(arr)

@autojit(backend='ast')
def func1(arg):
    return arg * 2

@autojit(backend='ast')
def func2(arg):
    return func1(arg + 1)

# ______________________________________________________________________

class TestASTExternCall(test_support.ASTTestCase):
    def test_call_zeros_like(self):
        testarr = numpy.array([1., 2, 3, 4, 5], dtype=numpy.double)
        testfn = self.jit(argtypes = [double[:]], restype = double[:])(
            call_zeros_like)
        print((sys.getrefcount(testarr)))
        result = testfn(testarr)
        print((sys.getrefcount(testarr)))
        print((sys.getrefcount(result)))
        self.assertTrue((result == numpy.zeros_like(testarr)).all())

    def test_call_len(self):
        testarr = numpy.arange(10.)
        testfn = self.jit(argtypes = [double[:]], restype = long_)(
            call_len)
        self.assertEqual(testfn(testarr), 10)

    def test_numba_calls_numba(self):
        self.assertEqual(func2(3), 8)
        self.assertEqual(func2(2+3j), (3+3j)*2)

# ______________________________________________________________________

if __name__ == "__main__":
#    TestASTExternCall('test_call_zeros_like').debug()
    unittest.main()

# ______________________________________________________________________
# End of test_extern_call.py
