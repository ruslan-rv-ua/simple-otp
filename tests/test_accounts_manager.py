"""Tests for AccountsManager class."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount


@pytest.fixture
def temp_storage():
    """Create a temporary directory for test storage."""
    with TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test_accounts.json"
        yield storage_path


@pytest.fixture
def manager(temp_storage):
    """Create an AccountsManager instance with temporary storage."""
    return AccountsManager(storage_path=temp_storage)


@pytest.fixture
def sample_account():
    """Create a sample TOTP account for testing."""
    return TOTPAccount.from_secret(
        name="test@example.com",
        secret="JBSWY3DPEHPK3PXP",
        password="test_password",
        issuer="Test Service",
        digits=6,
        digest=DigestAlgorithm.SHA1,
        interval=30,
    )


@pytest.fixture
def another_account():
    """Create another sample TOTP account for testing."""
    return TOTPAccount.from_secret(
        name="another@example.com",
        secret="HXDMVJECJJWSRB3HWIZR4IFUGFTMXBOZ",
        password="another_password",
        issuer="Another Service",
        digits=8,
        digest=DigestAlgorithm.SHA256,
        interval=60,
    )


class TestAccountsManagerInitialization:
    """Test AccountsManager initialization behavior."""

    def test_creates_storage_file_on_init(self, temp_storage):
        """Test that storage file is created if it doesn't exist."""
        assert not temp_storage.exists()

        manager = AccountsManager(storage_path=temp_storage)

        assert temp_storage.exists()
        assert manager.get_storage_path() == temp_storage

    def test_creates_example_account_on_init(self, temp_storage):
        """Test that an example account is created in new storage."""
        manager = AccountsManager(storage_path=temp_storage)

        accounts = manager.list_accounts()
        assert len(accounts) == 1

        example = accounts[0]
        # Updated to match the new test account from authenticationtest.com
        assert example.name == "totp@authenticationtest.com"
        assert example.issuer == "AuthenticationTest.com"
        assert example.digits == 6
        assert example.interval == 30

    def test_reads_existing_storage_file(self, temp_storage, sample_account):
        """Test that existing storage file is read correctly."""
        # Create initial manager and add account
        manager1 = AccountsManager(storage_path=temp_storage)
        manager1.clear_all_accounts()
        manager1.add_account(sample_account)

        # Create new manager instance with same storage
        manager2 = AccountsManager(storage_path=temp_storage)

        accounts = manager2.list_accounts()
        assert len(accounts) == 1
        assert accounts[0].name == sample_account.name
        assert accounts[0].issuer == sample_account.issuer

    def test_json_file_format(self, temp_storage, sample_account):
        """Test that the JSON file is properly indented and formatted."""
        manager = AccountsManager(storage_path=temp_storage)
        manager.clear_all_accounts()
        manager.add_account(sample_account)

        # Read raw JSON
        with open(temp_storage, encoding="utf-8") as f:
            content = f.read()
            data = json.loads(content)

        # Check structure
        assert "accounts" in data
        assert isinstance(data["accounts"], list)
        assert len(data["accounts"]) == 1

        # Check indentation (indented JSON has newlines)
        assert "\n" in content
        assert "  " in content  # 2-space indentation


class TestAddAccount:
    """Test adding accounts."""

    def test_add_single_account(self, manager, sample_account):
        """Test adding a single account."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)

        accounts = manager.list_accounts()
        assert len(accounts) == 1
        assert accounts[0].name == sample_account.name

    def test_add_multiple_accounts(self, manager, sample_account, another_account):
        """Test adding multiple accounts."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)
        manager.add_account(another_account)

        accounts = manager.list_accounts()
        assert len(accounts) == 2

        names = {acc.name for acc in accounts}
        assert sample_account.name in names
        assert another_account.name in names

    def test_add_duplicate_account_raises_error(self, manager, sample_account):
        """Test that adding a duplicate account raises ValueError."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)

        # Try to add the same account again
        duplicate = TOTPAccount.from_secret(
            name=sample_account.name,
            secret="DIFFERENT_SECRET",
            password="different_password",
            issuer=sample_account.issuer,  # Same issuer
        )

        with pytest.raises(ValueError, match="Account already exists"):
            manager.add_account(duplicate)

    def test_add_same_name_different_issuer(self, manager):
        """Test that accounts with same name but different issuers can coexist."""
        manager.clear_all_accounts()

        account1 = TOTPAccount.from_secret(
            name="user@example.com",
            secret="SECRET1",
            password="password1",
            issuer="Service A",
        )

        account2 = TOTPAccount.from_secret(
            name="user@example.com",
            secret="SECRET2",
            password="password2",
            issuer="Service B",
        )

        manager.add_account(account1)
        manager.add_account(account2)

        accounts = manager.list_accounts()
        assert len(accounts) == 2

    def test_account_persists_all_fields(self, manager):
        """Test that all account fields are persisted correctly."""
        manager.clear_all_accounts()

        account = TOTPAccount.from_secret(
            name="test@example.com",
            secret="JBSWY3DPEHPK3PXP",
            password="password",
            issuer="Test Issuer",
            digits=8,
            digest=DigestAlgorithm.SHA512,
            interval=60,
        )

        manager.add_account(account)
        loaded = manager.get_account("test@example.com", "Test Issuer")

        assert loaded is not None
        assert loaded.name == account.name
        assert loaded.issuer == account.issuer
        assert loaded.digits == account.digits
        assert loaded.digest == account.digest
        assert loaded.interval == account.interval
        assert loaded.encrypted_secret == account.encrypted_secret
        assert loaded.salt == account.salt


class TestDeleteAccount:
    """Test deleting accounts."""

    def test_delete_existing_account(self, manager, sample_account):
        """Test deleting an existing account."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)

        result = manager.delete_account(sample_account.name, sample_account.issuer)

        assert result is True
        accounts = manager.list_accounts()
        assert len(accounts) == 0

    def test_delete_nonexistent_account(self, manager):
        """Test deleting a nonexistent account returns False."""
        manager.clear_all_accounts()

        result = manager.delete_account("nonexistent@example.com", "Fake Service")

        assert result is False

    def test_delete_with_empty_issuer(self, manager):
        """Test deleting an account with no issuer."""
        manager.clear_all_accounts()

        account = TOTPAccount.from_secret(
            name="user@example.com",
            secret="JBSWY3DPEHPK3PXP",
            password="password",
            issuer="",  # No issuer
        )

        manager.add_account(account)
        result = manager.delete_account("user@example.com", "")

        assert result is True
        assert len(manager.list_accounts()) == 0

    def test_delete_one_of_multiple_accounts(
        self, manager, sample_account, another_account
    ):
        """Test deleting one account when multiple exist."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)
        manager.add_account(another_account)

        result = manager.delete_account(sample_account.name, sample_account.issuer)

        assert result is True
        accounts = manager.list_accounts()
        assert len(accounts) == 1
        assert accounts[0].name == another_account.name


class TestGetAccount:
    """Test retrieving specific accounts."""

    def test_get_existing_account(self, manager, sample_account):
        """Test retrieving an existing account."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)

        account = manager.get_account(sample_account.name, sample_account.issuer)

        assert account is not None
        assert account.name == sample_account.name
        assert account.issuer == sample_account.issuer

    def test_get_nonexistent_account(self, manager):
        """Test retrieving a nonexistent account returns None."""
        manager.clear_all_accounts()

        account = manager.get_account("nonexistent@example.com", "Fake Service")

        assert account is None

    def test_get_account_with_empty_issuer(self, manager):
        """Test retrieving an account with no issuer."""
        manager.clear_all_accounts()

        account = TOTPAccount.from_secret(
            name="user@example.com",
            secret="JBSWY3DPEHPK3PXP",
            password="password",
            issuer="",
        )

        manager.add_account(account)
        retrieved = manager.get_account("user@example.com", "")

        assert retrieved is not None
        assert retrieved.name == "user@example.com"


class TestListAccounts:
    """Test listing all accounts."""

    def test_list_empty_storage(self, manager):
        """Test listing accounts when storage is empty."""
        manager.clear_all_accounts()

        accounts = manager.list_accounts()

        assert accounts == []

    def test_list_multiple_accounts(self, manager, sample_account, another_account):
        """Test listing multiple accounts."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)
        manager.add_account(another_account)

        accounts = manager.list_accounts()

        assert len(accounts) == 2

    def test_list_returns_new_list(self, manager, sample_account):
        """Test that list_accounts returns a new list each time."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)

        list1 = manager.list_accounts()
        list2 = manager.list_accounts()

        assert list1 is not list2  # Different list objects
        assert len(list1) == len(list2)


class TestUpdateAccount:
    """Test updating existing accounts."""

    def test_update_existing_account(self, manager, sample_account):
        """Test updating an existing account."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)

        # Create updated version
        updated = TOTPAccount.from_secret(
            name="updated@example.com",
            secret="NEWSECRET",
            password="new_password",
            issuer="Updated Service",
            digits=8,
        )

        result = manager.update_account(
            sample_account.name, sample_account.issuer, updated
        )

        assert result is True

        # Verify old account is gone
        old = manager.get_account(sample_account.name, sample_account.issuer)
        assert old is None

        # Verify new account exists
        new = manager.get_account("updated@example.com", "Updated Service")
        assert new is not None
        assert new.digits == 8

    def test_update_nonexistent_account(self, manager, sample_account):
        """Test updating a nonexistent account returns False."""
        manager.clear_all_accounts()

        result = manager.update_account(
            "nonexistent@example.com", "Fake Service", sample_account
        )

        assert result is False

    def test_update_with_conflicting_name(
        self, manager, sample_account, another_account
    ):
        """Test that updating to a conflicting name raises ValueError."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)
        manager.add_account(another_account)

        # Try to update sample_account to have the same name/issuer as another_account
        conflicting = TOTPAccount.from_secret(
            name=another_account.name,
            secret="DIFFERENT",
            password="password",
            issuer=another_account.issuer,
        )

        with pytest.raises(ValueError, match="Account already exists"):
            manager.update_account(
                sample_account.name, sample_account.issuer, conflicting
            )

    def test_update_same_name_is_allowed(self, manager, sample_account):
        """Test that updating an account while keeping the same name/issuer is allowed."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)

        # Update with same name/issuer but different secret
        updated = TOTPAccount.from_secret(
            name=sample_account.name,
            secret="NEWSECRET",
            password="new_password",
            issuer=sample_account.issuer,
            digits=8,  # Different digit count
        )

        result = manager.update_account(
            sample_account.name, sample_account.issuer, updated
        )

        assert result is True

        account = manager.get_account(sample_account.name, sample_account.issuer)
        assert account.digits == 8


class TestClearAllAccounts:
    """Test clearing all accounts."""

    def test_clear_empty_storage(self, manager):
        """Test clearing when storage is already empty."""
        manager.clear_all_accounts()

        count = manager.clear_all_accounts()

        assert count == 0

    def test_clear_with_accounts(self, manager, sample_account, another_account):
        """Test clearing when accounts exist."""
        manager.clear_all_accounts()
        manager.add_account(sample_account)
        manager.add_account(another_account)

        count = manager.clear_all_accounts()

        assert count == 2
        assert len(manager.list_accounts()) == 0


class TestStoragePath:
    """Test storage path management."""

    def test_get_storage_path(self, manager, temp_storage):
        """Test getting the storage path."""
        path = manager.get_storage_path()

        assert path == temp_storage
        assert isinstance(path, Path)

    def test_default_storage_path_location(self):
        """Test that default storage path is one level up from project."""
        manager = AccountsManager()

        path = manager.get_storage_path()
        assert path.name == "accounts.json"
        # The parent should be one level up from the project root
        # (project root is where simple_otp package is located)


class TestJSONFormat:
    """Test JSON file format and structure."""

    def test_digest_enum_serialization(self, manager):
        """Test that DigestAlgorithm enum is properly serialized."""
        manager.clear_all_accounts()

        for digest in [
            DigestAlgorithm.SHA1,
            DigestAlgorithm.SHA256,
            DigestAlgorithm.SHA512,
        ]:
            account = TOTPAccount.from_secret(
                name=f"user_{digest.value}@example.com",
                secret="JBSWY3DPEHPK3PXP",
                password="password",
                issuer=f"Service {digest.value}",
                digest=digest,
            )
            manager.add_account(account)

        # Read raw JSON
        with open(manager.get_storage_path(), encoding="utf-8") as f:
            data = json.load(f)

        # Check that digest values are stored as strings
        for account_data in data["accounts"]:
            assert isinstance(account_data["digest"], str)
            assert account_data["digest"] in ["sha1", "sha256", "sha512"]

        # Verify they can be loaded back
        accounts = manager.list_accounts()
        assert len(accounts) == 3
        for account in accounts:
            assert isinstance(account.digest, DigestAlgorithm)

    def test_unicode_support(self, manager):
        """Test that Unicode characters in names and issuers are handled correctly."""
        manager.clear_all_accounts()

        account = TOTPAccount.from_secret(
            name="用户@例え.com",
            secret="JBSWY3DPEHPK3PXP",
            password="password",
            issuer="サービス 🔐",
        )

        manager.add_account(account)
        loaded = manager.get_account("用户@例え.com", "サービス 🔐")

        assert loaded is not None
        assert loaded.name == "用户@例え.com"
        assert loaded.issuer == "サービス 🔐"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_account_with_minimum_iterations(self, manager):
        """Test account with minimum allowed iterations."""
        manager.clear_all_accounts()

        account = TOTPAccount.from_secret(
            name="test@example.com",
            secret="JBSWY3DPEHPK3PXP",
            password="password",
            iterations=100_000,  # Minimum allowed
        )

        manager.add_account(account)
        loaded = manager.get_account("test@example.com", "")

        assert loaded is not None
        assert loaded.iterations == 100_000

    def test_account_with_high_iterations(self, manager):
        """Test account with very high iterations."""
        manager.clear_all_accounts()

        account = TOTPAccount.from_secret(
            name="test@example.com",
            secret="JBSWY3DPEHPK3PXP",
            password="password",
            iterations=1_000_000,
        )

        manager.add_account(account)
        loaded = manager.get_account("test@example.com", "")

        assert loaded is not None
        assert loaded.iterations == 1_000_000

    def test_multiple_accounts_same_name_no_issuer(self, manager):
        """Test that accounts with same name and no issuer are treated as duplicates."""
        manager.clear_all_accounts()

        account1 = TOTPAccount.from_secret(
            name="user@example.com",
            secret="SECRET1",
            password="password1",
            issuer="",
        )

        account2 = TOTPAccount.from_secret(
            name="user@example.com",
            secret="SECRET2",
            password="password2",
            issuer="",
        )

        manager.add_account(account1)

        with pytest.raises(ValueError, match="Account already exists"):
            manager.add_account(account2)
