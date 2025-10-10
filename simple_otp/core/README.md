# Core Module

This module contains the core business logic for the simple-otp application.

## Components

### `encryptor.py`
Provides encryption and decryption utilities for TOTP secrets using:
- **PBKDF2-HMAC-SHA256** for key derivation (600,000 iterations from `constants.PBKDF2_ITERATIONS`)
- **AES-256-GCM** for encryption

### `accounts_manager.py`
Manages TOTP accounts with JSON file persistence.

### `settings_manager.py`
Manages application settings with JSON persistence. See [Settings Documentation](../../docs/SETTINGS.md) for details.

### `authenticator.py`
Handles password authentication for encrypted account files. Provides centralized authentication logic with retry attempts.

### `recent_files_manager.py`
Manages the recent files list in application settings. Handles adding, removing, and clearing recent file entries with configurable maximum entries.

### `version_utils.py`
Utility module for retrieving application version from `pyproject.toml`.

### `i18n.py`
Internationalization support for multiple languages (English, Ukrainian).

## AccountsManager

The `AccountsManager` class handles all operations for managing TOTP accounts, including storage, retrieval, and modification.

### Storage Location

By default, accounts are stored in `accounts.json` one level up from the project folder. For example:
```
c:/dev/
├── simple-otp/          # Project folder
│   └── simple_otp/
└── accounts.json        # Accounts storage (one level up)
```

You can also specify a custom storage path:
```python
from pathlib import Path
manager = AccountsManager(storage_path=Path("custom/path/accounts.json"))
```

### Initial Setup

When you create an `AccountsManager` instance for the first time, it automatically:
1. Creates the `accounts.json` file if it doesn't exist
2. Adds a test account from [authenticationtest.com](https://authenticationtest.com/totpChallenge):
   - **Name**: `totp@authenticationtest.com`
   - **Issuer**: `AuthenticationTest.com`
   - **Password**: `example_password` (master password for encryption)
   - **Secret**: `I65VU7K5ZQL7WB4E` (publicly available test secret)

#### Testing the Default Account

You can verify the TOTP implementation works correctly by:
1. Opening the default account in the app (use password: `example_password`)
2. Copying the generated TOTP code
3. Visiting https://authenticationtest.com/totpChallenge
4. Logging in with:
   - **Email**: `totp@authenticationtest.com`
   - **Password**: `pa$$w0rd`
   - **MFA Code**: The TOTP code from the app

If authentication succeeds, your TOTP implementation is working correctly!

### Operations

#### Add Account
```python
from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.models.totp_account import TOTPAccount, DigestAlgorithm

manager = AccountsManager()

account = TOTPAccount.from_secret(
    name="user@example.com",
    secret="JBSWY3DPEHPK3PXP",
    password="my_password",
    issuer="Google",
    digits=6,
    digest=DigestAlgorithm.SHA1,
    interval=30,
)

manager.add_account(account)
```

#### Get Account
```python
account = manager.get_account("user@example.com", "Google")
if account:
    totp = account.get_totp("my_password")
    code = totp.now()
    print(f"Current code: {code}")
```

#### List All Accounts
```python
accounts = manager.list_accounts()
for account in accounts:
    print(account.get_display_name())
```

#### Update Account
```python
updated_account = TOTPAccount.from_secret(
    name="newemail@example.com",
    secret="NEWSECRET",
    password="my_password",
    issuer="Google",
)

success = manager.update_account(
    old_name="user@example.com",
    old_issuer="Google",
    new_account=updated_account
)
```

#### Delete Account
```python
deleted = manager.delete_account("user@example.com", "Google")
if deleted:
    print("Account deleted successfully")
```

#### Clear All Accounts
```python
count = manager.clear_all_accounts()
print(f"Cleared {count} accounts")
```

### JSON Format

The accounts are stored in an indented JSON format for readability:

```json
{
  "accounts": [
    {
      "name": "user@example.com",
      "encrypted_secret": "base64_encoded_encrypted_data",
      "salt": "base64_encoded_salt",
      "issuer": "Google",
      "digits": 6,
      "digest": "sha1",
      "interval": 30
    }
  ]
}
```

**Note**: Prior to recent refactoring, JSON files contained an `iterations` field. This field is now obsolete and is automatically removed when loading accounts. All encryption/decryption operations use the project-wide constant `PBKDF2_ITERATIONS` (600,000) defined in `simple_otp/constants.py`.

### Security Considerations

- **Secrets are encrypted**: All TOTP secrets are encrypted using AES-256-GCM with a password-derived key
- **Secure key derivation**: Uses PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP recommendation, defined in `constants.PBKDF2_ITERATIONS`)
- **Unique salts**: Each account has its own cryptographically secure salt
- **Password required**: You must provide the correct password to decrypt secrets and generate TOTP codes
- **Project-wide iterations**: All accounts use the same iteration count for consistency and security

### Error Handling

- **Duplicate accounts**: Adding an account with the same name and issuer raises `ValueError`
- **Invalid credentials**: Attempting to decrypt with wrong password raises `cryptography.exceptions.InvalidTag`
- **Missing file**: If the storage file is corrupted or missing, it will be recreated on next initialization
- **Invalid account data**: Account validation occurs during creation (see `TOTPAccount` documentation)

### Thread Safety

The `AccountsManager` is **not thread-safe**. If you need concurrent access, implement your own locking mechanism.

## Example Usage

See `example_accounts_manager_usage.py` for a complete example demonstrating all operations.

Run it with:
```cmd
uv run python -m simple_otp.core.example_accounts_manager_usage
```
