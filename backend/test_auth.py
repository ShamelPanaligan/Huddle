from auth import hash_password, verify_password, create_access_token, decode_access_token


def test_hash_password_differs_from_plaintext():
    hashed = hash_password("test123")
    assert hashed != "test123"


def test_verify_password_correct_returns_true():
    hashed = hash_password("test123")
    assert verify_password("test123", hashed) is True


def test_verify_password_incorrect_returns_false():
    hashed = hash_password("test123")
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token_returns_a_string():
    token = create_access_token(user_id=1)
    assert isinstance(token, str)


def test_decode_access_token_round_trip():
    token = create_access_token(user_id=42)
    result = decode_access_token(token)
    assert result == 42


def test_decode_access_token_garbage_input_returns_none():
    result = decode_access_token("this.is.not.a.real.token")
    assert result is None