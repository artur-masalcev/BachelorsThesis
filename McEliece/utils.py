import numpy as np


def is_invertible_F2(a):
    """
    Determine invertibility by Gaussian elimination
    """
    a = np.array(a, dtype=np.bool_)
    n = a.shape[0]
    for i in range(n):
        pivots = np.where(a[i:, i])[0]
        if len(pivots) == 0:
            return False

        # swap pivot
        piv = i + pivots[0]
        row = a[piv, i:].copy()
        a[piv, i:] = a[i, i:]
        a[i, i:] = row

        # eliminate
        for j in range(i + 1, n):
            if a[j, i]:
                a[j, i:] ^= row  # XOR for elimination in GF(2)

    return True


def generate_s_matrix(k, GF2m):
    while True:
        candidate = np.random.randint(2, size=(k, k))
        if is_invertible_F2(candidate):
            return GF2m(candidate)


def generate_p_matrix(n, GF2m):
    permutation_matrix = np.identity(n, dtype=int)

    # Shuffle the rows to obtain a random permutation matrix.
    np.random.shuffle(permutation_matrix)

    return GF2m(permutation_matrix)
