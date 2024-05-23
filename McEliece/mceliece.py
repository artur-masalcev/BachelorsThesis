import numpy as np
from galois import GF, irreducible_poly
import random

from McEliece.goppa_code_utils import generate_x_matrix, generate_y_matrix, generate_z_matrix, generate_g_matrx
from McEliece.utils import generate_s_matrix, generate_p_matrix
from OAEP.oaep import oaep_encode


class McEliece:
    def __init__(self, n, t, m):
        self.n = n
        self.t = t
        self.m = m
        self.k = n - t * m
        self.GF2m = GF(2 ** self.m)
        self.L = None
        self.g_poly = None
        self.S = None
        self.G = None
        self.P = None
        self.G_prime = None

        self._generate_key_pair()

    def _generate_key_pair(self):
        """

        :return:
        """
        # Generate the Goppa polynomial
        self.g_poly = irreducible_poly(order=2 ** self.m, degree=self.t, method="random")

        # Pick a subset L
        self.L = []
        for element in self.GF2m.elements:
            if self.g_poly(element) != 0:
                self.L.append(element)
            if len(self.L) == self.n:
                break

        # Generate parity matrix H = XYZ
        g_coefficients = [int(coefficient) for coefficient in self.g_poly.coeffs]

        X = generate_x_matrix(g_coefficients, self.GF2m)
        Y = generate_y_matrix(self.L, self.t, self.GF2m)
        Z = generate_z_matrix(self.L, self.g_poly, self.GF2m)

        H = X @ Y @ Z

        # Generate public-key matrix G'
        self.S = generate_s_matrix(self.k, self.GF2m)
        self.G = generate_g_matrx(H, self.GF2m)
        self.P = generate_p_matrix(self.n, self.GF2m)

        self.G_prime = self.S @ self.G @ self.P

    def encrypt(self, plaintext):
        """
        Encrypts given plaintext message
        :param plaintext: message to encrypt
        :return: encrypted message
        """

        # Calculate the mask size
        mask_length_in_bytes = self.k // 8
        padded_message = oaep_encode(plaintext.encode('ascii'), b'', mask_length_in_bytes)

        # Convert bytes to a list of bits
        bit_list = [int(bit) for byte in padded_message for bit in format(byte, '08b')]

        # Convert the list to a binary array
        msg = np.array(bit_list, dtype=np.uint8)

        # Encrypt the binary array
        y = np.array(self.GF2m(msg) @ self.G_prime)

        e = list(range(self.n))
        random.shuffle(e)

        for err_loc in e[: self.t]:
            y[err_loc] ^= 1

        return y