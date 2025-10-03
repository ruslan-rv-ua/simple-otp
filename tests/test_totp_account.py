"""Tests for TOTPAccount model."""

import pyotp
import pytest

from simple_otp.core.encryptor import Encryptor
from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount


class TestDigestAlgorithm:
    """Tests for DigestAlgorithm enum."""

    def test_digest_algorithm_values(self):
        """Test that digest algorithm enum has correct values."""
        assert DigestAlgorithm.SHA1 == "sha1"
        assert DigestAlgorithm.SHA256 == "sha256"
        assert DigestAlgorithm.SHA512 == "sha512"


class TestEncryptor:
    """Tests for Encryptor class."""

    def test_generate_salt(self):
        """Test salt generation."""
        salt = Encryptor.generate_salt()
        assert isinstance(salt, str)
        assert len(salt) > 0

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption work correctly."""
        plain_secret = "JBSWY3DPEHPK3PXP"
        password = "test_password_123"
        salt = Encryptor.generate_salt()

        # Encrypt
        encrypted = Encryptor.encrypt(plain_secret, password, salt)
        assert isinstance(encrypted, str)
        assert encrypted != plain_secret

        # Decrypt
        decrypted = Encryptor.decrypt(encrypted, password, salt)
        assert decrypted == plain_secret

    def test_decrypt_with_wrong_password_fails(self):
        """Test that decryption fails with wrong password."""
        plain_secret = "JBSWY3DPEHPK3PXP"
        password = "correct_password"
        wrong_password = "wrong_password"
        salt = Encryptor.generate_salt()

        encrypted = Encryptor.encrypt(plain_secret, password, salt)

        # Should raise an exception when decrypting with wrong password
        with pytest.raises(Exception):  # cryptography.exceptions.InvalidTag
            Encryptor.decrypt(encrypted, wrong_password, salt)

    def test_encrypt_uses_project_constant(self):
        """Test that encryption uses the project-wide PBKDF2_ITERATIONS constant."""
        from simple_otp.constants import PBKDF2_ITERATIONS

        plain_secret = "JBSWY3DPEHPK3PXP"
        password = "test_password"
        salt = Encryptor.generate_salt()

        encrypted = Encryptor.encrypt(plain_secret, password, salt)
        decrypted = Encryptor.decrypt(encrypted, password, salt)

        assert decrypted == plain_secret
        assert PBKDF2_ITERATIONS == 600_000  # Verify the constant value


class TestTOTPAccount:
    """Tests for TOTPAccount dataclass."""

    @pytest.fixture
    def valid_salt(self):
        """Generate a valid salt."""
        return Encryptor.generate_salt()

    @pytest.fixture
    def valid_encrypted_secret(self):
        """Generate a valid encrypted secret."""
        plain_secret = "JBSWY3DPEHPK3PXP"
        password = "test_password"
        salt = Encryptor.generate_salt()
        return Encryptor.encrypt(plain_secret, password, salt)

    @pytest.fixture
    def test_password(self):
        """Test password for encryption/decryption."""
        return "test_password_123"

    @pytest.fixture
    def encrypted_account_data(self, test_password):
        """Generate encrypted account data."""
        plain_secret = "JBSWY3DPEHPK3PXP"
        salt = Encryptor.generate_salt()
        encrypted_secret = Encryptor.encrypt(plain_secret, test_password, salt)
        return {
            "plain_secret": plain_secret,
            "encrypted_secret": encrypted_secret,
            "salt": salt,
            "password": test_password,
        }

    def test_create_account_with_defaults(self, encrypted_account_data):
        """Test creating account with minimal required parameters."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="user@example.com",
        )

        assert account.encrypted_secret == encrypted_account_data["encrypted_secret"]
        assert account.salt == encrypted_account_data["salt"]
        assert account.digits == 6
        assert account.digest == DigestAlgorithm.SHA1
        assert account.interval == 30
        assert account.name == "user@example.com"
        assert account.issuer == ""

    def test_create_account_with_all_parameters(self, encrypted_account_data):
        """Test creating account with all parameters."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="user@example.com",
            issuer="GitHub",
            digits=8,
            digest=DigestAlgorithm.SHA256,
            interval=60,
        )

        assert account.encrypted_secret == encrypted_account_data["encrypted_secret"]
        assert account.salt == encrypted_account_data["salt"]
        assert account.name == "user@example.com"
        assert account.issuer == "GitHub"
        assert account.digits == 8
        assert account.digest == DigestAlgorithm.SHA256
        assert account.interval == 60

    def test_empty_encrypted_secret_raises_error(self, valid_salt):
        """Test that empty encrypted_secret raises ValueError."""
        with pytest.raises(ValueError, match="encrypted_secret cannot be empty"):
            TOTPAccount(encrypted_secret="", salt=valid_salt, name="test")

    def test_empty_salt_raises_error(self, valid_encrypted_secret):
        """Test that empty salt raises ValueError."""
        with pytest.raises(ValueError, match="salt cannot be empty"):
            TOTPAccount(encrypted_secret=valid_encrypted_secret, salt="", name="test")

    def test_empty_name_raises_error(self, valid_encrypted_secret, valid_salt):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            TOTPAccount(
                encrypted_secret=valid_encrypted_secret, salt=valid_salt, name=""
            )

    def test_invalid_digits_raises_error(self, valid_encrypted_secret, valid_salt):
        """Test that invalid digits value raises ValueError."""
        with pytest.raises(ValueError, match="digits must be 6 or 8"):
            TOTPAccount(
                encrypted_secret=valid_encrypted_secret,
                salt=valid_salt,
                name="test",
                digits=4,
            )

    def test_negative_interval_raises_error(self, valid_encrypted_secret, valid_salt):
        """Test that negative interval raises ValueError."""
        with pytest.raises(ValueError, match="interval must be positive"):
            TOTPAccount(
                encrypted_secret=valid_encrypted_secret,
                salt=valid_salt,
                name="test",
                interval=-10,
            )

    def test_zero_interval_raises_error(self, valid_encrypted_secret, valid_salt):
        """Test that zero interval raises ValueError."""
        with pytest.raises(ValueError, match="interval must be positive"):
            TOTPAccount(
                encrypted_secret=valid_encrypted_secret,
                salt=valid_salt,
                name="test",
                interval=0,
            )

    def test_get_display_name_with_issuer_and_name(self, encrypted_account_data):
        """Test display name with both issuer and name."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="user@example.com",
            issuer="GitHub",
        )
        assert account.get_display_name() == "GitHub (user@example.com)"

    def test_get_display_name_with_issuer_only(self, encrypted_account_data):
        """Test display name with only issuer."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="user@example.com",
            issuer="GitHub",
        )
        # With both issuer and name, should show both
        assert account.get_display_name() == "GitHub (user@example.com)"

    def test_get_display_name_with_name_only(self, encrypted_account_data):
        """Test display name with only name."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="user@example.com",
        )
        assert account.get_display_name() == "user@example.com"

    def test_sha256_digest(self, encrypted_account_data):
        """Test using SHA256 digest algorithm."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="test",
            digest=DigestAlgorithm.SHA256,
        )
        assert account.digest == DigestAlgorithm.SHA256

    def test_sha512_digest(self, encrypted_account_data):
        """Test using SHA512 digest algorithm."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="test",
            digest=DigestAlgorithm.SHA512,
        )
        assert account.digest == DigestAlgorithm.SHA512

    def test_8_digit_code(self, encrypted_account_data):
        """Test creating account with 8-digit codes."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="test",
            digits=8,
        )
        assert account.digits == 8

    def test_custom_interval(self, encrypted_account_data):
        """Test creating account with custom interval."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="test",
            interval=60,
        )
        assert account.interval == 60

    def test_get_totp_returns_correct_instance(self, encrypted_account_data):
        """Test that get_totp returns a valid pyotp.TOTP instance."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="user@example.com",
            issuer="GitHub",
        )

        totp = account.get_totp(encrypted_account_data["password"])

        assert isinstance(totp, pyotp.TOTP)
        assert totp.digits == account.digits
        assert totp.interval == account.interval
        assert totp.name == account.name
        assert totp.issuer == account.issuer

    def test_get_totp_generates_valid_code(self, encrypted_account_data):
        """Test that get_totp generates a valid TOTP code."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="test_account",
        )

        totp = account.get_totp(encrypted_account_data["password"])
        code = totp.now()

        assert isinstance(code, str)
        assert len(code) == account.digits
        assert code.isdigit()

    def test_get_totp_with_wrong_password_raises_error(self, encrypted_account_data):
        """Test that get_totp fails with wrong password."""
        account = TOTPAccount(
            encrypted_secret=encrypted_account_data["encrypted_secret"],
            salt=encrypted_account_data["salt"],
            name="test_account",
        )

        with pytest.raises(Exception):  # cryptography.exceptions.InvalidTag
            account.get_totp("wrong_password")

    def test_get_totp_with_8_digits(self, test_password):
        """Test TOTP generation with 8-digit codes."""
        plain_secret = "JBSWY3DPEHPK3PXP"
        salt = Encryptor.generate_salt()
        encrypted_secret = Encryptor.encrypt(plain_secret, test_password, salt)

        account = TOTPAccount(
            encrypted_secret=encrypted_secret, salt=salt, name="test", digits=8
        )

        totp = account.get_totp(test_password)
        code = totp.now()

        assert len(code) == 8
        assert code.isdigit()

    def test_get_totp_with_sha256(self, test_password):
        """Test TOTP generation with SHA256 algorithm."""
        plain_secret = "JBSWY3DPEHPK3PXP"
        salt = Encryptor.generate_salt()
        encrypted_secret = Encryptor.encrypt(plain_secret, test_password, salt)

        account = TOTPAccount(
            encrypted_secret=encrypted_secret,
            salt=salt,
            name="test",
            digest=DigestAlgorithm.SHA256,
        )

        totp = account.get_totp(test_password)
        code = totp.now()

        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()


class TestTOTPAccountFromSecret:
    """Tests for TOTPAccount.from_secret classmethod."""

    @pytest.fixture
    def test_password(self):
        """Test password for encryption/decryption."""
        return "test_password_123"

    @pytest.fixture
    def test_secret(self):
        """Test TOTP secret."""
        return "JBSWY3DPEHPK3PXP"

    def test_from_secret_with_defaults(self, test_secret, test_password):
        """Test creating account from secret with default parameters."""
        account = TOTPAccount.from_secret(
            name="user@example.com", secret=test_secret, password=test_password
        )

        assert account.name == "user@example.com"
        assert account.issuer == ""
        assert account.digits == 6
        assert account.digest == DigestAlgorithm.SHA1
        assert account.interval == 30
        assert account.encrypted_secret  # Should have encrypted secret
        assert account.salt  # Should have generated salt

    def test_from_secret_with_all_parameters(self, test_secret, test_password):
        """Test creating account from secret with all parameters."""
        account = TOTPAccount.from_secret(
            name="user@example.com",
            secret=test_secret,
            password=test_password,
            issuer="GitHub",
            digits=8,
            digest=DigestAlgorithm.SHA256,
            interval=60,
        )

        assert account.name == "user@example.com"
        assert account.issuer == "GitHub"
        assert account.digits == 8
        assert account.digest == DigestAlgorithm.SHA256
        assert account.interval == 60

    def test_from_secret_generates_unique_salts(self, test_secret, test_password):
        """Test that from_secret generates unique salts for each account."""
        account1 = TOTPAccount.from_secret(
            name="test1", secret=test_secret, password=test_password
        )
        account2 = TOTPAccount.from_secret(
            name="test2", secret=test_secret, password=test_password
        )

        assert account1.salt != account2.salt
        assert account1.encrypted_secret != account2.encrypted_secret

    def test_from_secret_encrypts_correctly(self, test_secret, test_password):
        """Test that from_secret encrypts the secret correctly."""
        account = TOTPAccount.from_secret(
            name="test", secret=test_secret, password=test_password
        )

        # Should be able to decrypt and use the secret
        totp = account.get_totp(test_password)
        code = totp.now()

        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()

    def test_from_secret_empty_secret_raises_error(self, test_password):
        """Test that empty secret raises ValueError."""
        with pytest.raises(ValueError, match="secret cannot be empty"):
            TOTPAccount.from_secret(name="test", secret="", password=test_password)

    def test_from_secret_empty_name_raises_error(self, test_secret, test_password):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            TOTPAccount.from_secret(name="", secret=test_secret, password=test_password)

    def test_from_secret_invalid_digits_raises_error(self, test_secret, test_password):
        """Test that invalid digits value raises ValueError."""
        with pytest.raises(ValueError, match="digits must be 6 or 8"):
            TOTPAccount.from_secret(
                name="test", secret=test_secret, password=test_password, digits=4
            )

    def test_from_secret_totp_matches_reference(self, test_secret, test_password):
        """Test that from_secret produces same TOTP as direct PyOTP."""
        account = TOTPAccount.from_secret(
            name="test", secret=test_secret, password=test_password
        )

        # Get TOTP from account
        account_totp = account.get_totp(test_password)
        account_code = account_totp.now()

        # Get TOTP directly from PyOTP with same secret
        reference_totp = pyotp.TOTP(test_secret)
        reference_code = reference_totp.now()

        assert account_code == reference_code

    def test_from_secret_with_sha256_digest(self, test_secret, test_password):
        """Test from_secret with SHA256 digest algorithm."""
        account = TOTPAccount.from_secret(
            name="test",
            secret=test_secret,
            password=test_password,
            digest=DigestAlgorithm.SHA256,
        )

        assert account.digest == DigestAlgorithm.SHA256

        totp = account.get_totp(test_password)
        code = totp.now()

        assert len(code) == 6
        assert code.isdigit()

    def test_from_secret_with_sha512_digest(self, test_secret, test_password):
        """Test from_secret with SHA512 digest algorithm."""
        account = TOTPAccount.from_secret(
            name="test",
            secret=test_secret,
            password=test_password,
            digest=DigestAlgorithm.SHA512,
        )

        assert account.digest == DigestAlgorithm.SHA512

        totp = account.get_totp(test_password)
        code = totp.now()

        assert len(code) == 6
        assert code.isdigit()

    def test_from_secret_with_8_digits(self, test_secret, test_password):
        """Test from_secret with 8-digit codes."""
        account = TOTPAccount.from_secret(
            name="test", secret=test_secret, password=test_password, digits=8
        )

        assert account.digits == 8

        totp = account.get_totp(test_password)
        code = totp.now()

        assert len(code) == 8
        assert code.isdigit()

    def test_from_secret_with_custom_interval(self, test_secret, test_password):
        """Test from_secret with custom interval."""
        account = TOTPAccount.from_secret(
            name="test", secret=test_secret, password=test_password, interval=60
        )

        assert account.interval == 60

        totp = account.get_totp(test_password)
        assert totp.interval == 60

    def test_from_secret_wrong_password_fails(self, test_secret, test_password):
        """Test that wrong password fails to decrypt."""
        account = TOTPAccount.from_secret(
            name="test", secret=test_secret, password=test_password
        )

        with pytest.raises(Exception):  # cryptography.exceptions.InvalidTag
            account.get_totp("wrong_password")
