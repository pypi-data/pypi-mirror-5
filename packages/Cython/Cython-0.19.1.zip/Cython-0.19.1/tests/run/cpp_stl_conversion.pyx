# tag: cpp

import sys
from libcpp.map cimport map
from libcpp.set cimport set as cpp_set
from libcpp.string cimport string
from libcpp.pair cimport pair
from libcpp.vector cimport vector
from libcpp.list cimport list as cpp_list

py_set = set
py_xrange = xrange
py_unicode = unicode

cdef string add_strings(string a, string b):
    return a + b

def normalize(bytes b):
    if sys.version_info[0] >= 3:
        return b.decode("ascii")
    else:
        return b

def test_string(o):
    """
    >>> normalize(test_string("abc".encode('ascii')))
    'abc'
    >>> normalize(test_string("abc\\x00def".encode('ascii')))
    'abc\\x00def'
    """
    cdef string s = o
    return s

def test_encode_to_string(o):
    """
    >>> normalize(test_encode_to_string('abc'))
    'abc'
    >>> normalize(test_encode_to_string('abc\\x00def'))
    'abc\\x00def'
    """
    cdef string s = o.encode('ascii')
    return s

def test_encode_to_string_cast(o):
    """
    >>> normalize(test_encode_to_string_cast('abc'))
    'abc'
    >>> normalize(test_encode_to_string_cast('abc\\x00def'))
    'abc\\x00def'
    """
    s = <string>o.encode('ascii')
    return s

def test_unicode_encode_to_string(unicode o):
    """
    >>> normalize(test_unicode_encode_to_string(py_unicode('abc')))
    'abc'
    >>> normalize(test_unicode_encode_to_string(py_unicode('abc\\x00def')))
    'abc\\x00def'
    """
    cdef string s = o.encode('ascii')
    return s

def test_string_call(a, b):
    """
    >>> normalize(test_string_call("abc".encode('ascii'), "xyz".encode('ascii')))
    'abcxyz'
    """
    return add_strings(a, b)

def test_int_vector(o):
    """
    >>> test_int_vector([1, 2, 3])
    [1, 2, 3]
    >>> test_int_vector((1, 10, 100))
    [1, 10, 100]
    >>> test_int_vector(py_xrange(1,10,2))
    [1, 3, 5, 7, 9]
    >>> test_int_vector([10**20])       #doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    OverflowError: ...
    """
    cdef vector[int] v = o
    return v

def test_string_vector(s):
    """
    >>> list(map(normalize, test_string_vector('ab cd ef gh'.encode('ascii'))))
    ['ab', 'cd', 'ef', 'gh']
    """
    cdef vector[string] cpp_strings = s.split()
    return cpp_strings

cdef list convert_string_vector(vector[string] vect):
    return vect

def test_string_vector_temp_funcarg(s):
    """
    >>> list(map(normalize, test_string_vector_temp_funcarg('ab cd ef gh'.encode('ascii'))))
    ['ab', 'cd', 'ef', 'gh']
    """
    return convert_string_vector(s.split())

def test_double_vector(o):
    """
    >>> test_double_vector([1, 2, 3])
    [1.0, 2.0, 3.0]
    >>> test_double_vector([10**20])
    [1e+20]
    """
    cdef vector[double] v = o
    return v

def test_pair(o):
    """
    >>> test_pair((1, 2))
    (1, 2.0)
    """
    cdef pair[long, double] p = o
    return p

def test_list(o):
    """
    >>> test_list([1, 2, 3])
    [1, 2, 3]
    """
    cdef cpp_list[int] l = o
    return l

def test_set(o):
    """
    >>> sorted(test_set([1, 2, 3]))
    [1, 2, 3]
    >>> sorted(test_set([1, 2, 3, 3]))
    [1, 2, 3]
    >>> type(test_set([])) is py_set
    True
    """
    cdef cpp_set[long] s = o
    return s

def test_map(o):
    """
    >>> test_map({1: 1.0, 2: 0.5, 3: 0.25})
    {1: 1.0, 2: 0.5, 3: 0.25}
    """
    cdef map[int, double] m = o
    return m

def test_nested(o):
    """
    >>> test_nested({})
    {}
    >>> test_nested({(1.0, 2.0): [1, 2, 3], (1.0, 0.5): [1, 10, 100]})
    {(1.0, 2.0): [1, 2, 3], (1.0, 0.5): [1, 10, 100]}
    """
    cdef map[pair[double, double], vector[int]] m = o
    return m
