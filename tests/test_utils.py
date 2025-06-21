import string
from password_manager.utils import generate_password

def test_length_and_type():
    pwd = generate_password(20)
    assert isinstance(pwd, str)
    assert len(pwd) == 20

def test_complexity():
    pwd = generate_password(100)
    assert any(c.islower() for c in pwd)
    assert any(c.isupper() for c in pwd)
    assert any(c.isdigit() for c in pwd)
    punctuation = set(string.punctuation)
    assert any(c in punctuation for c in pwd)
