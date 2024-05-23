import math
import numpy as np


def matrix_to_byte_array(binary_matrix):
    # Flatten the matrix to a 1D array
    flat_array = binary_matrix.flatten()

    # Calculate the number of full bytes
    num_full_bytes = math.ceil(len(flat_array) / 8)

    byte_array = bytearray(num_full_bytes)

    # Fill the byte array with values
    for i in range(num_full_bytes):
        # Slice 8 bits
        byte = flat_array[i*8:(i+1)*8]
        # Convert bits to a single byte
        byte_array[i] = np.packbits(byte)[0]

    # Handle the remainder if there are leftover bits
    remainder = len(flat_array) % 8
    if remainder != 0:
        # Slice the remaining bits
        byte = flat_array[-remainder:]
        byte = np.pad(byte, (0, 8 - remainder), 'constant')  # Pad to make 8 bits
        byte_array[-1] = np.packbits(byte)[0]

    return byte_array


def byte_array_to_matrix(byte_array, dims):
    # Number of bits
    num_bits = dims[0] * dims[1]

    # Convert byte array to a list of bits
    bit_list = []
    for byte in byte_array:
        # Get 8 bits from each byte
        bit_list.extend([int(bit) for bit in f'{byte:08b}'])

    # Truncate the list to the exact number of bits needed (in case of padding)
    bit_list = bit_list[:num_bits]

    # Convert list of bits back to a numpy array
    bit_array = np.array(bit_list, dtype=np.uint8)

    # Reshape the array to the original dimensions
    matrix = bit_array.reshape(dims)

    return matrix
