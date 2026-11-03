import pytest
from backend.app.core.security import get_password_hash, verify_password, create_access_token
import jwt
from backend.app.core.config import settings

def test_password_hashing():
    raw_pwd = "EnterprisePassword!2025"
    hashed = get_password_hash(raw_pwd)
    assert hashed != raw_pwd
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_flow():
    payload = {"sub": "user_12345", "email": "test@example.com"}
    token = create_access_token(payload)
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == "user_12345"
    assert decoded["email"] == "test@example.com"
