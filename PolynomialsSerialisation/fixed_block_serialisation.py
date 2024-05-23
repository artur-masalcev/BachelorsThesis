import sympy
import random
from typing import List
import math


def polynomial_to_array(poly):
    coefficients = poly.all_coeffs()
    return [int(c) for c in coefficients]


def random_polynomial(degree, coeff_range):
    """
    Generates a random polynomial of a specified degree with coefficients in the specified range [0, coeff_range).

    Args:
    degree (int): The degree of the polynomial.
    coeff_range (int): The maximum value for the coefficients (exclusive).

    Returns:
    sympy.Poly: A polynomial with random coefficients.
    """
    x = sympy.symbols('x')
    coefficients = [random.randint(0, coeff_range - 1) for _ in range(degree + 1)]
    polynomial = sum(coeff * x ** i for i, coeff in enumerate(coefficients))
    return sympy.poly(polynomial)


def compress_polynomial(coefficients: List[int], n: int) -> bytes:
    """
    Serialises the given polynomial coefficients to a compressed form
    :param coefficients: integer array of coefficients
    :param n: modulo of coefficients (would be q for NTRUEncrypt public key)
    :return: compressed polynomial
    """
    # Calculate bits needed per coefficient
    b = math.ceil(math.log2(n))

    # Initialize the bit stream
    bit_stream = 0
    current_bit_length = 0

    # Pack each coefficient into the bit stream
    for coefficient in coefficients:
        bit_stream <<= b
        bit_stream |= coefficient
        current_bit_length += b

    # Convert the bit stream into bytes
    # Calculate how many full bytes are in the bit stream
    byte_count = (current_bit_length + 7) // 8

    # Create a byte array
    byte_array = bytearray(byte_count)

    # Fill the byte array from the bit stream
    for i in range(byte_count - 1, -1, -1):
        byte_array[i] = bit_stream & 0xFF  # Mask the lowest 8 bits
        bit_stream >>= 8  # Shift right by 8 bits

    return bytes(byte_array)


def decompress_polynomial(compressed_bytes: bytes, n: int, length: int) -> List[int]:
    """
    Decompresses the given compressed polynomial
    """
    # Calculate bits needed per coefficient
    b = math.ceil(math.log2(n))

    # Convert bytes back into a bit stream
    bit_stream = 0
    for byte in compressed_bytes:
        bit_stream = (bit_stream << 8) | byte

    # Extract coefficients from the bit stream
    coefficients = []
    # We'll use a mask to extract 'b' bits at a time
    mask = (1 << b) - 1

    # Extract exactly 'length' coefficients
    for _ in range(length):
        # Extract the last 'b' bits (current coefficient)
        coefficient = (bit_stream >> (b * (_))) & mask
        coefficients.append(coefficient)

    # Reverse the list to restore the original order since they are extracted from least to most significant
    coefficients.reverse()

    return coefficients
