"""TOTP Account data model with encrypted secret support."""

from dataclasses import dataclass
from enum import StrEnum

import pyotp

from simple_otp.core.encryptor import Encryptor


class DigestAlgorithm(StrEnum):
    """Supported digest algorithms for TOTP generation."""

    SHA1 = "sha1"
    SHA256 = "sha256"
    SHA512 = "sha512"


@dataclass
class TOTPAccount:
    """
    TOTP account model with encrypted secret storage.

    Based on pyotp.totp.TOTP class parameters:
    - digits: number of digits in TOTP code (typically 6 or 8)
    - digest: hash algorithm (SHA1, SHA256, or SHA512)
    - name: account name (e.g., email or username) - REQUIRED
    - issuer: service name (e.g., "Google", "GitHub")
    - interval: time interval in seconds (typically 30)

    Encryption parameters:
    - encrypted_secret: base64-encoded encrypted TOTP secret
    - salt: base64-encoded cryptographic salt for key derivation

    Note:
        PBKDF2 iterations are defined project-wide in constants.PBKDF2_ITERATIONS
    """

    name: str

    # Encrypted secret and encryption parameters (base64 encoded strings)
    encrypted_secret: str
    salt: str

    # Public TOTP parameters
    issuer: str = ""
    digits: int = 6
    digest: DigestAlgorithm = DigestAlgorithm.SHA1
    interval: int = 30

    def __post_init__(self):
        """Validate the account parameters."""
        if not self.encrypted_secret:
            raise ValueError("encrypted_secret cannot be empty")

        if not self.salt:
            raise ValueError("salt cannot be empty")

        if not self.name:
            raise ValueError("name cannot be empty")

        if self.digits not in (6, 8):
            raise ValueError("digits must be 6 or 8")

        if self.interval <= 0:
            raise ValueError("interval must be positive")

        if not isinstance(self.digest, DigestAlgorithm):
            raise ValueError(
                f"digest must be a DigestAlgorithm, got {type(self.digest)}"
            )

    @classmethod
    def from_secret(
        cls,
        name: str,
        secret: str,
        password: str,
        issuer: str = "",
        digits: int = 6,
        digest: DigestAlgorithm = DigestAlgorithm.SHA1,
        interval: int = 30,
    ) -> "TOTPAccount":
        """
        Create a TOTPAccount from a plain TOTP secret.

        Args:
            name: Account name (e.g., email or username) - REQUIRED
            secret: Plain TOTP secret (base32 encoded string)
            password: User's password to encrypt the secret
            issuer: Service name (e.g., "Google", "GitHub")
            digits: Number of digits in TOTP code (6 or 8)
            digest: Hash algorithm (SHA1, SHA256, or SHA512)
            interval: Time interval in seconds (typically 30)

        Returns:
            TOTPAccount instance with encrypted secret

        Raises:
            ValueError: If secret is empty or parameters are invalid

        Note:
            Uses PBKDF2_ITERATIONS constant for key derivation.
        """
        if not secret:
            raise ValueError("secret cannot be empty")

        # Generate a cryptographically secure salt
        salt = Encryptor.generate_salt()

        # Encrypt the secret
        encrypted_secret = Encryptor.encrypt(secret, password, salt)

        # Create and return the account instance
        return cls(
            name=name,
            encrypted_secret=encrypted_secret,
            salt=salt,
            issuer=issuer,
            digits=digits,
            digest=digest,
            interval=interval,
        )

    def get_display_name(self) -> str:
        """Get a display-friendly name for this account."""
        if self.issuer and self.name:
            return f"{self.issuer} ({self.name})"
        elif self.issuer:
            return self.issuer
        else:
            return self.name

    def get_totp(self, password: str) -> pyotp.TOTP:
        """
        Get a PyOTP TOTP instance for this account.

        Args:
            password: User's password to decrypt the secret

        Returns:
            pyotp.TOTP instance configured with this account's parameters

        Raises:
            cryptography.exceptions.InvalidTag: If password is incorrect

        Note:
            Uses PBKDF2_ITERATIONS constant for key derivation.
        """
        # Decrypt the secret
        plain_secret = Encryptor.decrypt(self.encrypted_secret, password, self.salt)

        # Create and return PyOTP TOTP instance
        return pyotp.TOTP(
            s=plain_secret,
            digits=self.digits,
            digest=self.digest,
            name=self.name,
            issuer=self.issuer if self.issuer else None,
            interval=self.interval,
        )
