import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

def derive_key(password: str, salt: bytes, iterations: int = 390_000) -> bytes:
    """
    Derive a symmetric key from the master password + salt.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def generate_salt(length: int = 16) -> bytes:
    """
    Returns a cryptographically strong random salt.
    """
    return os.urandom(length)

def get_fernet(key: bytes) -> Fernet:
    """
    Wrap the raw key into a Fernet instance for encryption/decryption.
    """
    return Fernet(key)
