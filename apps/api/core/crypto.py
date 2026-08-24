import json
import base64
import hashlib
from cryptography.fernet import Fernet
from config import settings

# Derive a stable 32-byte url-safe base64 key from the application's secret_key
_key_bytes = hashlib.sha256(settings.secret_key.encode("utf-8")).digest()
_fernet_key = base64.urlsafe_b64encode(_key_bytes)
_cipher = Fernet(_fernet_key)


def encrypt_dict(data: dict) -> str:
    """Encrypts a dictionary into a Fernet token string."""
    json_bytes = json.dumps(data).encode("utf-8")
    return _cipher.encrypt(json_bytes).decode("utf-8")


def decrypt_dict(token: str) -> dict:
    """Decrypts a Fernet token string back into a dictionary."""
    json_bytes = _cipher.decrypt(token.encode("utf-8"))
    return json.loads(json_bytes.decode("utf-8"))
