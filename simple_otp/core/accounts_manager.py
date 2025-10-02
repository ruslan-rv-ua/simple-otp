"""Accounts manager for persisting TOTP accounts to JSON storage."""

import json
from pathlib import Path

from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount


class AccountsManager:
    """
    Manages TOTP accounts with JSON file persistence.

    Accounts are stored in an indented JSON file one level up from the project folder.
    If the file doesn't exist on initialization, an example account is created.
    """

    def __init__(self, storage_path: Path | None = None, auto_create: bool = True):
        """
        Initialize the accounts manager.

        Args:
            storage_path: Optional custom path for the JSON file.
                         If None, defaults to ../accounts.json
                         (one level up from project).
            auto_create: If True, automatically create initial storage
                        with example account.
                        If False, storage must be created manually.
        """
        if storage_path is None:
            # Get the project root (where simple_otp package is located)
            project_root = Path(__file__).parent.parent.parent
            # Go one level up and create accounts.json
            self._storage_path = project_root.parent / "accounts.json"
        else:
            self._storage_path = storage_path

        # Initialize storage if it doesn't exist (only if auto_create is True)
        if auto_create and not self._storage_path.exists():
            self._create_initial_storage()

    def _create_initial_storage(self) -> None:
        """Create initial storage file with an example account."""
        # Create an example account with a known password for demonstration
        # Uses test TOTP account from https://authenticationtest.com/totpChallenge
        # Email: totp@authenticationtest.com
        # Secret: I65VU7K5ZQL7WB4E
        # This can be used to verify the TOTP implementation works correctly
        example_password = "example_password"
        example_account = TOTPAccount.from_secret(
            name="totp@authenticationtest.com",
            secret="I65VU7K5ZQL7WB4E",  # Test secret from authenticationtest.com
            password=example_password,
            issuer="AuthenticationTest.com",
            digits=6,
            digest=DigestAlgorithm.SHA1,
            interval=30,
        )

        # Save to file
        self._save_accounts([example_account])

    def _load_accounts(self) -> list[TOTPAccount]:
        """
        Load all accounts from the JSON file.

        Returns:
            List of TOTPAccount objects

        Raises:
            FileNotFoundError: If the storage file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        with open(self._storage_path, encoding="utf-8") as f:
            data = json.load(f)

        accounts = []
        for account_data in data.get("accounts", []):
            # Convert digest string back to DigestAlgorithm enum
            digest_str = account_data.get("digest", "sha1")
            account_data["digest"] = DigestAlgorithm(digest_str)

            account = TOTPAccount(**account_data)
            accounts.append(account)

        return accounts

    def _save_accounts(self, accounts: list[TOTPAccount]) -> None:
        """
        Save all accounts to the JSON file.

        Args:
            accounts: List of TOTPAccount objects to save
        """
        # Convert accounts to dictionaries
        accounts_data = []
        for account in accounts:
            account_dict = {
                "name": account.name,
                "encrypted_secret": account.encrypted_secret,
                "salt": account.salt,
                "iterations": account.iterations,
                "issuer": account.issuer,
                "digits": account.digits,
                "digest": account.digest.value,  # Convert enum to string
                "interval": account.interval,
            }
            accounts_data.append(account_dict)

        # Write to file with indentation for readability
        data = {"accounts": accounts_data}
        with open(self._storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_account(self, account: TOTPAccount) -> None:
        """
        Add a new account to storage.

        Args:
            account: TOTPAccount to add

        Raises:
            ValueError: If an account with the same name and issuer already exists
        """
        accounts = self._load_accounts()

        # Check for duplicates
        for existing in accounts:
            if existing.name == account.name and existing.issuer == account.issuer:
                raise ValueError(
                    f"Account already exists: {account.get_display_name()}"
                )

        accounts.append(account)
        self._save_accounts(accounts)

    def delete_account(self, name: str, issuer: str = "") -> bool:
        """
        Delete an account from storage.

        If this is the last account, the storage file will be deleted.

        Args:
            name: Account name to delete
            issuer: Issuer of the account to delete (empty string if no issuer)

        Returns:
            True if account was deleted, False if not found
        """
        accounts = self._load_accounts()
        original_count = len(accounts)

        # Filter out the account to delete
        accounts = [
            acc for acc in accounts if not (acc.name == name and acc.issuer == issuer)
        ]

        if len(accounts) < original_count:
            # If this was the last account, delete the storage file
            if len(accounts) == 0:
                if self._storage_path.exists():
                    self._storage_path.unlink()
            else:
                self._save_accounts(accounts)
            return True

        return False

    def get_account(self, name: str, issuer: str = "") -> TOTPAccount | None:
        """
        Get a specific account by name and issuer.

        Args:
            name: Account name
            issuer: Issuer of the account (empty string if no issuer)

        Returns:
            TOTPAccount if found, None otherwise
        """
        accounts = self._load_accounts()

        for account in accounts:
            if account.name == name and account.issuer == issuer:
                return account

        return None

    def list_accounts(self) -> list[TOTPAccount]:
        """
        Get all accounts from storage.

        Returns:
            List of all TOTPAccount objects (empty list if storage doesn't exist)
        """
        if not self._storage_path.exists():
            return []
        return self._load_accounts()

    def update_account(
        self, old_name: str, old_issuer: str, new_account: TOTPAccount
    ) -> bool:
        """
        Update an existing account.

        Args:
            old_name: Current account name
            old_issuer: Current account issuer
            new_account: Updated TOTPAccount object

        Returns:
            True if account was updated, False if not found

        Raises:
            ValueError: If the new account name/issuer conflicts with
                       another existing account
        """
        accounts = self._load_accounts()
        account_found = False

        for i, account in enumerate(accounts):
            if account.name == old_name and account.issuer == old_issuer:
                account_found = True

                # Check if the new name/issuer conflicts with another account
                if old_name != new_account.name or old_issuer != new_account.issuer:
                    for other_account in accounts:
                        if (
                            other_account.name == new_account.name
                            and other_account.issuer == new_account.issuer
                            and other_account is not account
                        ):
                            raise ValueError(
                                "Account already exists: "
                                f"{new_account.get_display_name()}"
                            )

                # Update the account
                accounts[i] = new_account
                break

        if account_found:
            self._save_accounts(accounts)
            return True

        return False

    def clear_all_accounts(self) -> int:
        """
        Remove all accounts from storage.

        Returns:
            Number of accounts that were removed
        """
        accounts = self._load_accounts()
        count = len(accounts)
        self._save_accounts([])
        return count

    def get_storage_path(self) -> Path:
        """
        Get the path to the JSON storage file.

        Returns:
            Path object pointing to the storage file
        """
        return self._storage_path

    def storage_exists(self) -> bool:
        """
        Check if the storage file exists.

        Returns:
            True if the storage file exists, False otherwise
        """
        return self._storage_path.exists()

    def has_accounts(self) -> bool:
        """
        Check if there are any accounts in storage.

        Returns:
            True if storage exists and contains at least one account, False otherwise
        """
        if not self.storage_exists():
            return False

        try:
            accounts = self._load_accounts()
            return len(accounts) > 0
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def create_initial_account(self, password: str) -> TOTPAccount:
        """
        Create and save an initial default account with the given password.

        Args:
            password: Password to encrypt the account secret

        Returns:
            The created TOTPAccount

        Raises:
            ValueError: If accounts already exist
        """
        if self.has_accounts():
            raise ValueError("Accounts already exist")

        # Create a default test account from
        # https://authenticationtest.com/totpChallenge
        # This allows users to test the TOTP implementation with
        # a publicly available test account
        # Email: totp@authenticationtest.com
        # Secret: I65VU7K5ZQL7WB4E
        # Users can verify the generated codes against the website:
        # https://authenticationtest.com/totpChallenge
        default_account = TOTPAccount.from_secret(
            name="totp@authenticationtest.com",
            secret="I65VU7K5ZQL7WB4E",  # Test secret from authenticationtest.com
            password=password,
            issuer="AuthenticationTest.com",
            digits=6,
            digest=DigestAlgorithm.SHA1,
            interval=30,
        )

        # Save to file
        self._save_accounts([default_account])
        return default_account

    def verify_password(self, password: str) -> bool:
        """
        Verify a password by attempting to decrypt the first account.

        Args:
            password: Password to verify

        Returns:
            True if password is correct (can decrypt first account), False otherwise
        """
        if not self.has_accounts():
            return False

        try:
            accounts = self._load_accounts()
            if len(accounts) == 0:
                return False

            # Try to decrypt the first account
            first_account = accounts[0]
            _ = first_account.get_totp(password)  # This will raise if password is wrong
            return True
        except Exception:
            # Any exception means password is incorrect or decryption failed
            return False
