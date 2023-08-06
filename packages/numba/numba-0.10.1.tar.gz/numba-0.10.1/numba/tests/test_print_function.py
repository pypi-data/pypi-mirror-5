from __future__ import print_function

import sys
import unittest
import StringIO

from numba import *

@autojit(backend='ast')
def print_(value):
    print(value)

@autojit(backend='ast', nopython=True)
def print_nopython(value):
    print("value", end=" ")
    print(value)

@autojit(backend='ast')
def print_to_stream(stream, value):
    print(value, file=stream)

@autojit(backend='ast')
def print_no_newline(stream, value):
    print(value, end=' ', file=stream)

class TestPrint(unittest.TestCase):
    def test_print(self):
        out = sys.stdout
        sys.stdout = temp_out = StringIO.StringIO()
        try:
            print_(10)
            print_(10.0)
            print_("hello!")
        finally:
            sys.stdout = out

        data = temp_out.getvalue()
        assert data == "10\n10.0\nhello!\n", repr(data)

    def test_print_stream(self):
        temp_out = StringIO.StringIO()
        print_to_stream(temp_out, 13.2)
        data = temp_out.getvalue()
        assert data == "13.2\n", repr(data)

    def test_print_no_newline(self):
        temp_out = StringIO.StringIO()
        print_no_newline(temp_out, 14.1)
        data = temp_out.getvalue()
        assert data == "14.1 ", repr(data)

if __name__ == "__main__":
    # The following isn't currently supported.  See issue #147
    #(https://github.com/numba/numba/issues/147).

    #print_nopython(10)
    TestPrint('test_print_stream').debug()
    unittest.main()
