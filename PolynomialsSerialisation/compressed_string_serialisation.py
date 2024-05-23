from sympy import symbols, Poly
import base64
import zlib


def poly_to_base64(poly, apply_compression=False):
    """
    Stringifies the given polynomial to a base64 encoded string.
    :param poly: polynomial to serialise
    :param apply_compression: if set to 'True', applies compression algorithm
    :return: base64 encoded string representing given polynomial
    """
    # Create comma-separated representation of the polynomial
    coefficients = poly.all_coeffs()
    string_separated_coefficients = ','.join(map(str, coefficients))

    # Get the bytes representation
    encoded_bytes = string_separated_coefficients.encode()

    # Apply compression if needed
    if apply_compression:
        compressed_data = zlib.compress(encoded_bytes)
        print(f"Size of uncompressed data: {len(encoded_bytes)}")
        print(f"Size of compressed data {len(compressed_data)}")

        return base64.b64encode(compressed_data).decode()
    else:
        return base64.b64encode(encoded_bytes).decode()


def base64_to_poly(base64_str, compression_applied=False):
    """
    Converts stringified polynomial back to Sympy object
    :param base64_str: stringified polynomial
    :param compression_applied: set to 'True' if compression was applied
    :return: Sympy Poly object representing the given polynomial
    """
    x = symbols('x')

    # Decode the Base64 string
    decoded_bytes = base64.b64decode(base64_str)

    # Decompress the data if needed
    if compression_applied:
        decoded_bytes = zlib.decompress(decoded_bytes)

    decoded_string = decoded_bytes.decode('utf-8')

    # Parse a stringified array to an array of integers
    coefficients = [int(x) for x in decoded_string.split(',')]
    return Poly(sum(coefficients[i] * x ** (len(coefficients) - 1 - i) for i in range(len(coefficients))), x)
