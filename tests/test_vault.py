import json
import pytest
from pathlib import Path
from password_manager import vault
from password_manager.crypto import derive_key, generate_salt

@pytest.fixture(autouse=True)
def tmp_vault_path(monkeypatch, tmp_path):
    fake = tmp_path / "vault.dat"
    monkeypatch.setattr(vault, "VAULT_PATH", fake)
    yield

def test_init_and_load_empty():
    master = "myMaster!"
    vault.init_vault(master)
    assert vault.VAULT_PATH.exists()

    # load should give empty dict
    data = vault.load_vault(master)
    assert data == {}

def test_save_and_reload():
    master = "xyz"
    vault.init_vault(master)
    d = vault.load_vault(master)
    d["foo"] = {"username": "u", "password": "p"}
    vault.save_vault(master, d)

    d2 = vault.load_vault(master)
    assert d2 == d
