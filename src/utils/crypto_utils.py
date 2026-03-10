import base64
import os
from pathlib import Path

from cryptography.fernet import Fernet

_KEY_FILE = Path.home() / ".jar-comparison" / ".key"


def _get_or_create_key() -> bytes:
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes()
    key = Fernet.generate_key()
    _KEY_FILE.write_bytes(key)
    return key


def encrypt(plaintext: str) -> str:
    if not plaintext:
        return ""
    f = Fernet(_get_or_create_key())
    return f.encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    if not ciphertext:
        return ""
    try:
        f = Fernet(_get_or_create_key())
        return f.decrypt(ciphertext.encode()).decode()
    except Exception:
        return ""
