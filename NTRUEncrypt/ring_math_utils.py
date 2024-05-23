from sympy import symbols, Poly


def truncate_mod(poly, n):
    """
    Truncates the given polynomial after the conventional
    multiplication to adhere to the rules of a truncated
    polynomial ring.
    :param poly: polynomial to truncate
    :param n: degree of the ring N
    :return: truncated polynomial
    """
    x = symbols('x')

    coefficients = poly.all_coeffs()
    degree = poly.degree()

    new_terms = {}

    for i, coefficient in enumerate(coefficients):
        current_degree = degree - i

        if current_degree >= n:
            new_degree = current_degree % n
        else:
            new_degree = current_degree

        if new_degree in new_terms:
            new_terms[new_degree] += coefficient
        else:
            new_terms[new_degree] = coefficient

    new_poly_expr = sum(coefficient * x ** degree for degree, coefficient in sorted(new_terms.items(), reverse=True))
    truncated_poly = Poly(new_poly_expr, x)

    return truncated_poly


def modulo_poly(poly, n):
    """
    Takes modulo n of the given polynomial
    :param poly: polynomial to take modulo of
    :param n: the number to take the modulo of
    :return: polynomial mod n
    """
    x = symbols('x')

    if not isinstance(poly, Poly):
        poly = Poly(poly, x)

    coefficients_mod_n = [coefficient % n for coefficient in poly.all_coeffs()]

    # Reconstruct the polynomial with the modified coefficients
    poly_mod = Poly(coefficients_mod_n, x, domain='ZZ').set_domain(poly.domain)

    return poly_mod
