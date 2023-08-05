import numpy as np
from numpy import ma

cimport numpy as np
from libc.math cimport cos

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

def window_1Dmean(data, l, t=None, method='hann', axis=0, parallel=True):
    
