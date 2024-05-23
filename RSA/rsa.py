import time
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization


def generate_rsa_key_pair(key_size):
    start_time = time.time()
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    end_time = time.time()
    print("Key generation time:", end_time - start_time, "seconds")

    public_key = private_key.public_key()
    return private_key, public_key


def encrypt_message(public_key, message):
    start_time = time.time()
    encrypted_message = public_key.encrypt(
        message.encode(),
        padding.OAEP(
            mgf=padding.mgf1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    end_time = time.time()
    print("Encryption time:", end_time - start_time, "seconds")
    return encrypted_message


def decrypt_message(private_key, encrypted_message):
    start_time = time.time()
    decrypted_message = private_key.decrypt(
        encrypted_message,
        padding.OAEP(
            mgf=padding.mgf1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    end_time = time.time()
    print("Decryption time:", end_time - start_time, "seconds")
    return decrypted_message.decode()


def measure_private_key_size(private_key):
    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return len(private_key_bytes)
