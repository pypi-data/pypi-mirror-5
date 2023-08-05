import numpy as np
cimport numpy as np
cimport cython

from cython.operator cimport dereference as deref

from libcpp cimport bool

cdef extern from "boost/random/mersenne_twister.hpp" namespace "boost::random" nogil:
    # random number generator
    cdef cppclass mt19937:
        #init
        mt19937() nogil
        #attributes

        #methods
        seed(unsigned long)


cdef extern from "rng_wrapper.hpp" nogil:
    # wrapper to distributions ...
    cdef cppclass rng_sampler[result_type]:
        #init
        rng_sampler(mt19937) nogil
        rng_sampler()  nogil
        # methods (gamma and exp are using rate param)
        result_type normal(result_type, result_type) nogil
        result_type gamma(result_type, result_type) nogil
        result_type uniform(result_type, result_type) nogil
        result_type exp(result_type) nogil
        result_type chisq(result_type) nogil

ctypedef mt19937 rng

