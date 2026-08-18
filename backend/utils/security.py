import hashlib
import hmac


def verify_paystack_signature(payload: bytes, signature: str, secret: str) -> bool:
    computed = hmac.new(
        secret.encode("utf-8"), payload, hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature)
