cimport cython
from libc.stdlib cimport rand, srand


@cython.boundscheck(False)
cpdef int hamming(char *str1, char *str2, int length):
    """ Compute the hamming distance between two strings
    """
    cdef int score = 0
    cdef int idx = 0
    cdef char ss1 = ' '
    cdef char ss2 = ' '
    for idx from 0 <= idx < length:
        ss1 = str1[idx]
        ss2 = str2[idx]
        if ss1 != '-' and ss2 != '-':
            score += (ss1 != ss2)

    return score

@cython.boundscheck(False)
cpdef float diversity(amp1, amp2, int overlap, int sub_sample, int seed):
    """ Compute the mean overlap diversity given two amplicons.
    """
    cdef int overlap_div = 0
    cdef float mean_overlap_div = 0.0
    cdef int idx = 0
    cdef int jdx = 0
    cdef int roverlap = 0
    cdef int len1 = len(amp1)
    cdef int len2 = len(amp2)
    cdef int pairs = len1 * len2

    if pairs < sub_sample:
        for idx from 0 <= idx < len1:
            read = amp1[idx]
            roverlap = len(read) - overlap
            read = read[roverlap:]
            for jdx from 0 <= jdx < len2:
                nread = amp2[jdx]
                nread = nread[:overlap]
                overlap_div += hamming(read, nread, overlap)

        mean_overlap_div = overlap_div / float(pairs) if pairs != 0.0\
                            else 0.0
    else:
        srand(seed)
        for idx from 0 <= idx < sub_sample:
            read = amp1[rand() % len1]
            nread = amp2[rand() % len2]
            roverlap = len(read) - overlap
            read = read[roverlap:]
            nread = nread[:overlap]
            overlap_div += hamming(read, nread, overlap)
        mean_overlap_div = overlap_div / float(sub_sample) if sub_sample != 0.0\
                            else 0.0

    return mean_overlap_div
