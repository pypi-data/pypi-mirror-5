# mode: error

cimport numpy as np

cdef void func(np.ndarray[np.double_t, ndim=1] myarray) nogil:
    pass

_ERRORS = u"""
5:15: Buffer may not be acquired without the GIL. Consider using memoryview slices instead.
"""
