import json
import base64
from pathlib import Path
from cryptography.fernet import InvalidToken

from password_manager.crypto import derive_key, generate_salt, get_fernet

VAULT_PATH = Path.home() / ".vault.dat"

def init_vault(master_password: str):
    """
    Create a fresh, empty vault encrypted under master_password.
    """
    if VAULT_PATH.exists():
        raise FileExistsError(f"Vault already exists at {VAULT_PATH}")
    salt = generate_salt()
    key = derive_key(master_password, salt)
    fernet = get_fernet(key)

    empty_blob = json.dumps({}).encode()
    token = fernet.encrypt(empty_blob).decode()

    data = {
        "salt": base64.urlsafe_b64encode(salt).decode(),
        "vault": token
    }
    with open(VAULT_PATH, "w") as f:
        json.dump(data, f)

def load_vault(master_password: str) -> dict:
    """
    Decrypt and return the vault as a Python dict.
    """
    if not VAULT_PATH.exists():
        raise FileNotFoundError("Vault not found. Run `init` first.")
    raw = json.loads(VAULT_PATH.read_text())
    salt = base64.urlsafe_b64decode(raw["salt"].encode())
    token = raw["vault"].encode()

    key = derive_key(master_password, salt)
    fernet = get_fernet(key)

    try:
        decrypted = fernet.decrypt(token)
    except InvalidToken:
        raise ValueError("Invalid master password or corrupted vault.")
    return json.loads(decrypted.decode())

def save_vault(master_password: str, vault: dict):
    """
    Encrypt the in-memory vault dict and overwrite the on-disk file.
    """
    raw = json.loads(VAULT_PATH.read_text())
    salt = base64.urlsafe_b64decode(raw["salt"].encode())

    key = derive_key(master_password, salt)
    fernet = get_fernet(key)

    token = fernet.encrypt(json.dumps(vault).encode()).decode()
    raw["vault"] = token

    with open(VAULT_PATH, "w") as f:
        json.dump(raw, f)
