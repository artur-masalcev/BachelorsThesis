from sympy import symbols, Poly


def decimal_to_ternary(n):
    """Convert a decimal number to ternary (base 3), returning as a list of digits."""
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(n % 3)
        n //= 3
    return digits[::-1]


def string_to_ternary(s, N):
    """Convert a string to a ternary code, using ASCII values."""
    s += chr(3)
    ternary_array = []
    for char in s:
        ascii_val = ord(char)
        ternary_digits = decimal_to_ternary(ascii_val)
        # Prefix with necessary zeros to ensure fixed length for each character
        ternary_digits = [0] * (5 - len(ternary_digits)) + ternary_digits
        ternary_array.extend(ternary_digits)

    for i in range(N - (len(s) * 5)):
        ternary_array.append(0)

    return ternary_array


def adjust_ternary(ternary_array):
    """Adjust the ternary array from 0, 1, 2 to -1, 0, 1."""
    return [x - 1 for x in ternary_array]


def ternary_to_poly(ternary_array, var='x'):
    """Convert an adjusted ternary array to a SymPy Poly object."""
    adjusted_array = ternary_array
    x = symbols(var)
    poly = Poly.from_list(adjusted_array[::-1], x)
    return poly


def poly_to_ternary(poly):
    """Convert a SymPy Poly object back to an original ternary array."""
    return [coefficient for coefficient in poly.all_coeffs()][::-1]


def ternary_to_decimal(ternary_array):
    """Convert a ternary number (as a list of digits) back to decimal."""
    return sum(digit * 3 ** i for i, digit in enumerate(ternary_array[::-1]))


def ternary_string_back(ternary_array):
    """Convert ternary code back to the original string."""
    original_string = ""
    i = 0
    while i < len(ternary_array):
        # Extract the ternary digits for one character
        ternary_digit_chunk = ternary_array[i:i + 5]  # Fixed length for each ASCII character
        decimal_value = ternary_to_decimal(ternary_digit_chunk)
        if decimal_value == 3:
            break
        original_string += chr(decimal_value)
        i += len(ternary_digit_chunk)
    return original_string[:-1]
