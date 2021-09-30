#cython: language_level=3
"""
Renormalization script:

    https://github.com/numpy/numpy/issues/16686

Ignore:
    >>> import xdev
    >>> import pathlib
    >>> fpath = pathlib.Path('~/misc/tests/python/renormalize_cython.pyx').expanduser()
    >>> renormalize_cython = xdev.import_module_from_pyx(fpath, recompile=True, verbose=3)
"""
import numpy as np

cimport numpy as np
cimport cython

from numpy.random.c_distributions cimport random_standard_uniform_fill
# from numpy.random.c_distributions cimport random_standard_uniform_fill_f



import numpy as np
cimport numpy as np
cimport cython
from cpython.pycapsule cimport PyCapsule_IsValid, PyCapsule_GetPointer
from libc.stdint cimport uint16_t, uint64_t
from numpy.random cimport bitgen_t
from numpy.random import PCG64

# from numpy.random cimport bitgen_t



def renormalize_demo_cython_v1(D, T) -> bool:
    import numpy as np
    energy = np.random.rand(D)
    for _ in range(T):
        probs = energy / energy.sum()
        # Do something with probs
        # Get probabilities for the next state and update
        updates = np.random.rand(D)
        energy = energy * updates
    return True


# @cython.boundscheck(False)
# @cython.cdivision(True)
# @cython.wraparound(False)
def renormalize_demo_cython_v2(int D, int T):
    # cdef np.ndarray[np.float64_t, ndim=1]
    cdef np.ndarray[np.float64_t, ndim=1] energy = np.random.rand(D)
    for _ in range(T):
        probs = energy / energy.sum()
        # Do something with probs
        # Get probabilities for the next state and update
        updates = np.random.rand(D)
        energy = energy * updates

    return True
    # cdef np.ndarray[np.float32_t, ndim=1] energy;
    # cdef np.ndarray[np.float32_t, ndim=1] probs;
    # cdef np.ndarray[np.float32_t, ndim=1] updates;
    # energy = np.random.rand(D).astype(np.float32)
    # # with nogil:
    # for _ in range(T):
    #     probs = energy / energy.sum()
    #     # Do something with probs
    #     # Get probabilities for the next state and update
    #     updates = np.random.rand(D).astype(np.float32)
    #     energy = energy * updates
    # return True


# @cython.boundscheck(False)
# @cython.wraparound(False)
# cdef renormalize_demo_cython_v3_backend(Py_ssize_t D, Py_ssize_t T):
    # return renormalize_demo_cython_v3_backend(D, T)
def renormalize_demo_cython_v3(D, T):
    # cdef const char *capsule_name = "BitGenerator"
    # cdef double[::1] random_values
    # cdef np.ndarray[np.float64_t, ndim=1] energy
    # cdef np.ndarray[np.float64_t, ndim=1] probs
    # cdef np.ndarray[np.float64_t, ndim=1] updates
    # cdef np.float64_t total
    rng = np.random
    energy = rng.rand(D)
    for _ in range(T):
        probs = energy / energy.sum()
        energy *= rng.rand(D)


@cython.boundscheck(False)
@cython.wraparound(False)
def uniforms(Py_ssize_t n):
    """
    Create an array of `n` uniformly distributed doubles.
    A 'real' distribution would want to process the values into
    some non-uniform distribution
    """
    cdef Py_ssize_t i
    cdef bitgen_t *rng
    cdef const char *capsule_name = "BitGenerator"
    cdef double[::1] random_values

    x = PCG64()
    capsule = x.capsule
    # 可选检查胶囊是否来自 BitGenerator
    if not PyCapsule_IsValid(capsule, capsule_name):
        raise ValueError("Invalid pointer to anon_func_state")
    # 投射指针
    rng = <bitgen_t *> PyCapsule_GetPointer(capsule, capsule_name)
    random_values = np.empty(n, dtype='float64')
    with x.lock, nogil:
        for i in range(n):
            # 调用函数
            random_values[i] = rng.next_double(rng.state)
    randoms = np.asarray(random_values)
    return randoms


# def uniforms_ex(bit_generator, Py_ssize_t n, dtype=np.float32):
#     """
#     Create an array of `n` uniformly distributed doubles via a "fill" function.

#     A 'real' distribution would want to process the values into
#     some non-uniform distribution

#     Parameters
#     ----------
#     bit_generator: BitGenerator instance
#     n: int
#         Output vector length
#     dtype: {str, dtype}, optional
#         Desired dtype, either 'd' (or 'float64') or 'f' (or 'float32'). The
#         default dtype value is 'd'
#     """
#     cdef Py_ssize_t i
#     cdef bitgen_t *rng
#     cdef const char *capsule_name = "BitGenerator"
#     cdef np.ndarray randoms

#     capsule = bit_generator.capsule
#     # Optional check that the capsule if from a BitGenerator
#     if not PyCapsule_IsValid(capsule, capsule_name):
#         raise ValueError("Invalid pointer to anon_func_state")
#     # Cast the pointer
#     rng = <bitgen_t *> PyCapsule_GetPointer(capsule, capsule_name)

#     _dtype = np.dtype(dtype)
#     randoms = np.empty(n, dtype=_dtype)
#     # if _dtype == np.float32:
#     #     with bit_generator.lock:
#     #         random_standard_uniform_fill_f(rng, n, <float*>np.PyArray_DATA(randoms))
#     # elif _dtype == np.float64:
#     with bit_generator.lock:
#         random_standard_uniform_fill(rng, n, <double*>np.PyArray_DATA(randoms))
#     # else:
#     #     raise TypeError('Unsupported dtype %r for random' % _dtype)
#     return randoms

