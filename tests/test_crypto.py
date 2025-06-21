import base64
from password_manager.crypto import derive_key, generate_salt, get_fernet

def test_derive_key_is_deterministic():
    pwd = "hunter2"
    salt = generate_salt()
    k1 = derive_key(pwd, salt)
    k2 = derive_key(pwd, salt)
    assert k1 == k2
    assert isinstance(k1, bytes)

def test_fernet_roundtrip():
    pwd = "pass123"
    salt = generate_salt()
    key = derive_key(pwd, salt)
    f = get_fernet(key)

    data = b"hello world"
    token = f.encrypt(data)
    assert isinstance(token, bytes)

    assert f.decrypt(token) == data
