# Implemented according to https://www.ietf.org/rfc/rfc2437.txt

from math import ceil
import os
import hashlib


def i2osp(x, xLen):
    """ Converts the integer x to an octet string of length xLen. """
    return x.to_bytes(xLen, byteorder='big')


def mgf1(Z, l, hash_func=hashlib.sha1):
    h_len = hash_func().digest_size

    if l > (2 ** 32) * h_len:
        raise ValueError("mask too long")

    t = b""

    for counter in range(ceil(l / h_len)):
        c = i2osp(counter, 4)
        t += hash_func(Z + c).digest()

    return t[:l]


def oaep_encode(M: bytes, L: bytes = b'', k: int = 128, hash_func=hashlib.sha1):
    h_len = hash_func().digest_size
    m_len = len(M)

    # 1. Hash the label L
    l_hash = hash_func(L).digest()

    # 2. Generate a padding string PS
    ps = b'\x00' * (k - m_len - 2 * h_len - 2)

    # 3. Concatenate lHash, PS, a single byte 0x01, and the message M
    db = l_hash + ps + b'\x01' + M

    # 4. Generate a random seed
    seed = os.urandom(h_len)

    # 5. Use MGF1 to generate a mask for the data block
    db_mask = mgf1(seed, k - h_len - 1, hash_func)

    # 6. Mask the data block
    masked_db = bytes(a ^ b for a, b in zip(db, db_mask))

    # 7. Use MGF1 to generate a mask for the seed
    seed_mask = mgf1(masked_db, h_len, hash_func)

    # 8. Mask the seed
    masked_seed = bytes(a ^ b for a, b in zip(seed, seed_mask))

    # 9. Concatenate maskedSeed and maskedDB to form the encoded message EM
    em = b'\x00' + masked_seed + masked_db
    return em


def oaep_decode(EM: bytes, L: bytes = b'', k: int = 128, hash_func=hashlib.sha1) -> bytes:
    h_len = hash_func().digest_size
    # 1. Hash the label L
    l_hash = hash_func(L).digest()

    # 2. Split the encoded message EM
    # EM = 0x00 || maskedSeed || maskedDB
    _, masked_seed, masked_db = EM[0], EM[1:h_len + 1], EM[h_len + 1:]

    # 3. Generate the seedMask which was used to mask the seed
    seed_mask = mgf1(masked_db, h_len, hash_func)

    # 4. Recover the seed
    seed = bytes(a ^ b for a, b in zip(masked_seed, seed_mask))

    # 5. Generate the dbMask which was used to mask the data block
    db_mask = mgf1(seed, k - h_len - 1, hash_func)

    # 6. Recover the data block DB
    db = bytes(a ^ b for a, b in zip(masked_db, db_mask))

    # 7. Split the data block into its parts
    l_hash_prime = db[:h_len]
    # Find the index of the 0x01 byte, which is the separator
    index_of_0x01 = db[h_len:].find(b'\x01') + h_len
    ps = db[h_len:index_of_0x01]  # This should only consist of 0x00 bytes
    separator = db[index_of_0x01]
    m = db[index_of_0x01 + 1:]

    # Verify the conditions
    if l_hash_prime != l_hash:
        raise ValueError("Decryption error: label hash does not match")
    if separator != 0x01:
        raise ValueError("Decryption error: incorrect separator")
    if any(x != 0x00 for x in ps):
        raise ValueError("Decryption error: padding string is not correct")

    # Find the index of the first non-zero byte after lHash_prime which should be the separator 0x01
    index_of_separator = db.find(b'\x01', h_len)

    # Extract the message M after the 0x01 separator
    m = db[index_of_separator + 1:]

    return m
