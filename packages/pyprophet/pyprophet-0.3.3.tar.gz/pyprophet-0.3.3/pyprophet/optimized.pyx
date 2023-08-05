#encoding: latin-1
cimport cython
cimport numpy as np
import  numpy as np


@cython.boundscheck(False)
@cython.wraparound(False)
def find_nearest_matches(np.float64_t[:] basis, np.float64_t[:] sample_points):
    cdef long num_basis = basis.shape[0]
    cdef long num_samples = sample_points.shape[0]
    result = np.zeros((num_samples,), dtype=np.int64)
    cdef long[:] view = result
    cdef long i, best_j
    cdef double sp_i, best_dist, dist
    for i in range(num_samples):
        sp_i = sample_points[i]
        best_dist = abs(basis[0] - sp_i)
        best_j = 0
        for j in range(1, num_basis):
            dist = abs(basis[j] - sp_i)
            if dist < best_dist:
                best_dist = dist
                best_j = j
        view[i] = best_j
    return result


@cython.boundscheck(False)
@cython.wraparound(False)
def find_top_ranked(np.int64_t[:] tg_ids, np.float64_t[:] scores):
    cdef long n = scores.shape[0]
    flags = np.zeros((n,), dtype=int)
    cdef long[:] view = flags
    cdef double current_max = scores[0]
    cdef long current_imax = 0
    cdef long current_tg_id = tg_ids[0]
    cdef long current_write_i=0
    cdef long i
    cdef long id_
    cdef double sc
    for i in range(tg_ids.shape[0]):
        id_ = tg_ids[i]
        sc = scores[i]
        if id_ != current_tg_id:
            current_tg_id = id_
            view[current_imax] = 1
            current_write_i += 1
            current_max = sc
            current_imax = i
            continue
        if sc > current_max:
            current_max = sc
            current_imax = i
    view[current_imax] = 1
    return flags
