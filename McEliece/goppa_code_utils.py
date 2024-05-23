import numpy as np
from scipy.linalg import null_space


def generate_x_matrix(coefficients, GF2m):
    t = len(coefficients) - 1
    x = np.zeros((t, t), dtype=int)

    for i in range(t):
        for j in range(i + 1):
            x[i, j] = coefficients[i - j]

    return GF2m(x)


def generate_y_matrix(L, t, GF2m):
    n = len(L)
    y = np.zeros((t, n), dtype=int)

    for i in range(t):
        for j in range(n):
            y[i, j] = L[j] ** i

    return GF2m(y)


def generate_z_matrix(L, g, GF2m):
    n = len(L)
    z = np.zeros((n, n), dtype=int)

    for i in range(n):
        z[i, i] = g(L[i]) ** -1

    return GF2m(z)


def generate_g_matrx(H, GF2m):
    # Convert H to binary for conforming with binary Goppa codes
    vectorized_rows = [np.column_stack([element.vector() for element in row]) for row in H]
    h_bin = np.vstack(vectorized_rows)

    h_bin_np = h_bin.view(np.ndarray).astype(np.int64)

    # Use scipy to find the nullspace of the matrix
    nullspace_h_bin = null_space(h_bin_np)
    nullspace_int = np.round(nullspace_h_bin).astype(np.int64) % 2

    return GF2m(nullspace_int).T

