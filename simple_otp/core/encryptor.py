"""Encryption and decryption utilities for TOTP secrets."""

import base64
import secrets

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Encryptor:
    """
    Handles encryption and decryption of TOTP secrets using password-based encryption.

    Uses PBKDF2-HMAC-SHA256 for key derivation and AES-256-GCM for encryption.
    """

    @staticmethod
    def generate_salt() -> str:
        """
        Generate a cryptographically secure 16-byte salt.

        Returns:
            Base64-encoded salt string
        """
        salt_bytes = secrets.token_bytes(16)
        return base64.b64encode(salt_bytes).decode("utf-8")

    @staticmethod
    def encrypt(
        plain_secret: str, password: str, salt: str, iterations: int = 600_000
    ) -> str:
        """
        Encrypt a TOTP secret using a password.

        Args:
            plain_secret: The plain text TOTP secret (base32 encoded string)
            password: User's password for encryption
            salt: Base64-encoded salt string
            iterations: Number of PBKDF2 iterations (default: 600,000)

        Returns:
            Base64-encoded encrypted secret (nonce + ciphertext)
        """
        # Decode salt from base64
        salt_bytes = base64.b64decode(salt)

        # Derive encryption key from password using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt_bytes,
            iterations=iterations,
        )
        key = kdf.derive(password.encode("utf-8"))

        # Encrypt the secret using AES-GCM
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)  # 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, plain_secret.encode("utf-8"), None)

        # Combine nonce and ciphertext for storage
        encrypted_bytes = nonce + ciphertext

        # Encode to base64 for string storage
        return base64.b64encode(encrypted_bytes).decode("utf-8")

    @staticmethod
    def decrypt(
        encrypted_secret: str, password: str, salt: str, iterations: int = 600_000
    ) -> str:
        """
        Decrypt a TOTP secret using a password.

        Args:
            encrypted_secret: Base64-encoded encrypted secret (nonce + ciphertext)
            password: User's password for decryption
            salt: Base64-encoded salt string
            iterations: Number of PBKDF2 iterations used during encryption

        Returns:
            Decrypted plain text TOTP secret

        Raises:
            cryptography.exceptions.InvalidTag: If password is incorrect
                                                or data is corrupted
        """
        # Decode salt and encrypted secret from base64
        salt_bytes = base64.b64decode(salt)
        encrypted_bytes = base64.b64decode(encrypted_secret)

        # Derive the same encryption key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=iterations,
        )
        key = kdf.derive(password.encode("utf-8"))

        # Split nonce and ciphertext
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]

        # Decrypt the secret
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext.decode("utf-8")
