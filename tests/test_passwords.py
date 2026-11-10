import pytest
from app.core.passwords import validate_policy, hash_password, verify_password, WeakPasswordError

def test_weak_password_rejected():
    with pytest.raises(WeakPasswordError):
        validate_policy("123", user_inputs=["test@example.com"])

def test_strong_password_accepted():
    # Не должно выбрасывать исключение
    validate_policy("SuperSecretPassword123!", user_inputs=["test@example.com"])

def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False