from backend.utils.security import verify_paystack_signature


def test_valid_signature():
    secret = "test_secret"
    payload = b'{"event":"charge.success","data":{"reference":"REF123"}}'
    import hashlib
    import hmac
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha512).hexdigest()
    assert verify_paystack_signature(payload, expected, secret) is True


def test_invalid_signature():
    secret = "test_secret"
    payload = b'{"event":"charge.success"}'
    assert verify_paystack_signature(payload, "wrong_signature", secret) is False


def test_empty_signature():
    assert verify_paystack_signature(b"", "", "secret") is False
