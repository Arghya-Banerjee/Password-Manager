import string
import random

def generate_password(length: int = 16) -> str:
    """
    Generate a cryptographically strong random password.
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(alphabet) for _ in range(length))
