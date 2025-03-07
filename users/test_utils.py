import pytest
from users.utils import PasswordHasher


def test_hash_password():
    password = "my_secure_password"
    hashed = PasswordHasher.hash_password(password)
    assert isinstance(hashed, str)
    assert len(hashed) == 32


def test_validate_password_correct():
    password = "my_secure_password"
    hashed = PasswordHasher.hash_password(password)
    assert PasswordHasher.validate_password(password, hashed)


def test_validate_password_incorrect():
    password = "my_secure_password"
    wrong_password = "another_password"
    hashed = PasswordHasher.hash_password(password)
    assert not PasswordHasher.validate_password(wrong_password, hashed)


def test_hash_password_empty():
    password = ""
    hashed = PasswordHasher.hash_password(password)
    assert hashed == "d41d8cd98f00b204e9800998ecf8427e"


def test_validate_password_empty():
    # Test validating an empty password
    password = ""
    hashed = PasswordHasher.hash_password(password)
    assert PasswordHasher.validate_password(password, hashed)
    assert not PasswordHasher.validate_password("non_empty_password", hashed)
