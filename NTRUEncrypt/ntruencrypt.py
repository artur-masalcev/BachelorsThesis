import base64

from sympy import symbols, Poly, invert, NotInvertible
from sympy.polys.specialpolys import random_poly
from sympy.polys.domains import ZZ, GF
import math

from NTRUEncrypt.plaintext_to_ternary_conversion_utils import string_to_ternary, ternary_to_poly, poly_to_ternary, \
    ternary_string_back
from NTRUEncrypt.ring_math_utils import truncate_mod, modulo_poly
from OAEP.oaep import oaep_encode, oaep_decode


class NTRUEncrypt:
    def __init__(self, N, p, q):
        self.N = N  # Degree of the polynomial
        self.p = p  # Small modulus
        self.q = q  # Large modulus
        self.f = None
        self.fp = None
        self.fq = None
        self.g = None
        self.h = None
        self.MAX_F_GENERATION_ITERATIONS = 5
        self.x = x = symbols('x')
        self.R_poly = Poly(x ** N - 1, domain=ZZ)
        self.mask_length_byes = (((self.N // 5) * 3) // 4) - 5

        self._generate_private_key()
        self._generate_public_key()

    def _generate_private_key(self):
        """
        Generates the polynomial components (f, f_p, f_q) of an NTRUEncrypt private key.
        This function attempts to generate a polynomial 'f' and its inverses 'f_p'
        and 'f_q' modulo two different primes 'p' and 'q', respectively.
        """

        for _ in range(self.MAX_F_GENERATION_ITERATIONS):
            f = random_poly(self.x, self.N - 1, -1, 1, domain=ZZ)
            try:
                # Find inverse f_p
                fp = invert(f, self.R_poly, domain=GF(self.p))

                # Find inverse f_q
                fq = invert(f, self.R_poly, domain=GF(2))
                inv_poly = invert(f, self.R_poly, domain=GF(2))
                e = int(math.log(self.q, 2))
                for i in range(1, e):
                    fq = ((2 * fq - f * fq ** 2) % self.R_poly).trunc(self.q)

                if fp != 0 and fq != 0:
                    self.g = random_poly(self.x, self.N - 1, -1, 1, domain=ZZ)
                    self.f = f
                    self.fp = fp
                    self.fq = fq
                    return

            except NotInvertible:
                pass

        return None, None, None

    def _generate_public_key(self):
        """
        Generates the NTRUEncrypt public key 'h'
        """

        pfq = truncate_mod(self.p * self.fq, self.N)
        pfqg = truncate_mod(pfq * self.g, self.N)
        self.h = modulo_poly(pfqg, self.q)

    def encrypt(self, plaintext):
        """
        Encrypts given plaintext message
        :param plaintext: message to encrypt
        :return: encrypted message
        """

        # At the moment polynomial conversion supports only ASCII format thus
        # the padded message should be base64 encoded
        padded_plaintext = oaep_encode(M=plaintext.encode('ascii'), L=b'', k=self.mask_length_byes)
        base64_encoded = base64.b64encode(padded_plaintext).decode('ascii')

        ternary_representation = string_to_ternary(base64_encoded, self.N - 1)
        poly_representation = ternary_to_poly(ternary_representation)

        r = Poly(random_poly(self.x, self.N - 1, -1, 1, domain=ZZ), self.x, domain=ZZ)
        r = truncate_mod(r * self.p * self.h, self.N)

        return modulo_poly(r + poly_representation, self.q)

    def decrypt(self, ciphertext):
        """
        Decrypts given ciphertext message
        :param ciphertext: ciphertext to decrypt
        :return: original message
        """
        a = modulo_poly(truncate_mod(self.f * ciphertext, self.N), self.q)

        adjusted_coefficients = []
        for coefficient in a.all_coeffs():
            # Perform the modular operation to ensure it's within [0, q)
            mod_coefficients = coefficient % self.q

            # Adjust coefficients that are greater than q/2 to fall within [-q/2, q/2]
            if mod_coefficients > self.q / 2:
                mod_coefficients -= self.q

            adjusted_coefficients.append(mod_coefficients)

        # Construct the adjusted polynomial
        a = sum(coefficient * self.x ** i for i, coefficient in enumerate(reversed(adjusted_coefficients)))

        b = modulo_poly(a, self.p)
        c = modulo_poly(truncate_mod(self.fp * b, self.N), self.p)

        ternary_from_poly = poly_to_ternary(Poly(c))

        plaintext = ternary_string_back(ternary_from_poly)
        original_message = oaep_decode(base64.b64decode(plaintext), L=b'', k=self.mask_length_byes)

        return original_message.decode('ascii')