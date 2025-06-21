import base64
import json
from cryptography.fernet import Fernet, InvalidToken

def _derive_key(master_password: str) -> bytes:
    # Simple static key derivation for example purposes.
    return base64.urlsafe_b64encode(master_password.encode("utf-8").ljust(32, b"0"))

def init_vault(master_password: str, path):
    if path.exists():
        raise FileExistsError("Vault already exists.")
    key = _derive_key(master_password)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps({}).encode("utf-8"))
    with open(path, "wb") as f:
        f.write(encrypted)

def load_vault(master_password: str, path):
    key = _derive_key(master_password)
    fernet = Fernet(key)
    with open(path, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = fernet.decrypt(encrypted)
    except InvalidToken:
        raise ValueError("Invalid master password.")
    return json.loads(decrypted.decode("utf-8"))

def save_vault(master_password: str, data: dict, path):
    key = _derive_key(master_password)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(json.dumps(data).encode("utf-8"))
    with open(path, "wb") as f:
        f.write(encrypted)
