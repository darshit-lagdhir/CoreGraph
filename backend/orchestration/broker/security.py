import hmac, hashlib

SECRET = b"COREGRAPH_SOVEREIGN_KEY_0xFF"


def sign_payload(payload: bytes) -> bytes:
    return hmac.new(SECRET, payload, hashlib.sha512).digest()


def verify_payload(payload: bytes, signature: bytes) -> bool:
    return hmac.compare_digest(sign_payload(payload), signature)
