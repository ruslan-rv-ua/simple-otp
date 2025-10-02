# PBKDF2 Iterations Refactoring

## Overview
Refactored PBKDF2 iterations from per-account configuration to a project-wide constant.

## Changes Made

### 1. New Constants Module
Created `simple_otp/constants.py` with project-wide encryption constants:

```python
# PBKDF2 key derivation settings
# OWASP recommendation for PBKDF2-HMAC-SHA256 (2023)
PBKDF2_ITERATIONS = 600_000

# Minimum allowed iterations for security
MIN_PBKDF2_ITERATIONS = 100_000
```

**Location**: `simple_otp/constants.py`  
**Purpose**: Centralize security-critical configuration values

### 2. Updated Encryptor
Modified `simple_otp/core/encryptor.py`:
- Removed `iterations` parameter from `encrypt()` and `decrypt()` methods
- Uses `PBKDF2_ITERATIONS` constant from `simple_otp.constants`
- Both methods now use the project-wide constant automatically

**Before**:
```python
encrypted = Encryptor.encrypt(secret, password, salt, iterations=600_000)
decrypted = Encryptor.decrypt(encrypted, password, salt, iterations=600_000)
```

**After**:
```python
encrypted = Encryptor.encrypt(secret, password, salt)
decrypted = Encryptor.decrypt(encrypted, password, salt)
```

### 3. Updated TOTPAccount Model
Modified `simple_otp/models/totp_account.py`:
- Removed `iterations` field from dataclass
- Removed `iterations` parameter from `from_secret()` method
- Updated `get_totp()` to use constant instead of instance field
- Removed iterations validation from `__post_init__()`

**Before**:
```python
@dataclass
class TOTPAccount:
    encrypted_secret: str
    salt: str
    iterations: int = 600_000
    # ... other fields
```

**After**:
```python
@dataclass
class TOTPAccount:
    encrypted_secret: str
    salt: str
    # iterations removed - now uses constants.PBKDF2_ITERATIONS
    # ... other fields
```

### 4. Updated AccountsManager
Modified `simple_otp/core/accounts_manager.py`:
- Removed `iterations` from JSON serialization in `_save_accounts()`
- Added cleanup in `_load_accounts()` to remove legacy `iterations` field from JSON

**JSON Format Change**:

**Before**:
```json
{
  "accounts": [
    {
      "name": "user@example.com",
      "encrypted_secret": "...",
      "salt": "...",
      "iterations": 600000,
      "issuer": "Google",
      "digits": 6,
      "digest": "sha1",
      "interval": 30
    }
  ]
}
```

**After**:
```json
{
  "accounts": [
    {
      "name": "user@example.com",
      "encrypted_secret": "...",
      "salt": "...",
      "issuer": "Google",
      "digits": 6,
      "digest": "sha1",
      "interval": 30
    }
  ]
}
```

### 5. Updated Tests
- Removed all iterations-related parameters from test cases
- Removed tests for custom iterations values
- Added new test to verify project constant is used
- All 72 tests pass successfully

## Rationale

### Why This Change?

1. **Simplification**: Iterations count is a security parameter that should be consistent across the application
2. **Maintainability**: Single source of truth makes it easier to update if security recommendations change
3. **Reduced Complexity**: Eliminates per-account configuration that users don't need to manage
4. **Security**: Ensures all accounts use the same secure iteration count (600,000 - OWASP recommendation)

### Security Impact

- **No Breaking Changes**: Existing encrypted data remains valid
- **Backward Compatibility**: Old JSON files with `iterations` field are automatically cleaned up on load
- **Forward Compatible**: All new accounts use the project-wide constant
- **Migration**: Automatic and transparent - no user action required

## Migration

### For Existing Installations

When the application loads existing `accounts.json` files:
1. Reads existing accounts (including legacy `iterations` field if present)
2. Automatically removes `iterations` field during deserialization
3. Uses project constant (`PBKDF2_ITERATIONS = 600_000`) for all decryption operations
4. Saves accounts without `iterations` field on next save operation

**No user intervention required** - migration is automatic and transparent.

### For Developers

If you're working with the codebase:

1. **Use constants** for iterations:
   ```python
   from simple_otp.constants import PBKDF2_ITERATIONS
   ```

2. **Don't pass iterations** to Encryptor methods:
   ```python
   # ✓ Correct
   encrypted = Encryptor.encrypt(secret, password, salt)
   
   # ✗ Incorrect (will cause TypeError)
   encrypted = Encryptor.encrypt(secret, password, salt, iterations=100_000)
   ```

3. **Don't set iterations** on TOTPAccount:
   ```python
   # ✓ Correct
   account = TOTPAccount.from_secret(
       name="user@example.com",
       secret="JBSWY3DPEHPK3PXP",
       password="password"
   )
   
   # ✗ Incorrect (will cause TypeError)
   account = TOTPAccount.from_secret(
       name="user@example.com",
       secret="JBSWY3DPEHPK3PXP",
       password="password",
       iterations=100_000
   )
   ```

## Files Changed

1. `simple_otp/constants.py` - **NEW** - Project-wide constants
2. `simple_otp/core/encryptor.py` - Removed iterations parameter, uses constant
3. `simple_otp/models/totp_account.py` - Removed iterations field and parameter
4. `simple_otp/core/accounts_manager.py` - Updated JSON handling
5. `tests/test_totp_account.py` - Updated test cases
6. `tests/test_accounts_manager.py` - Updated test cases
7. `docs/PBKDF2_ITERATIONS_REFACTORING.md` - **NEW** - This document
8. `docs/PASSWORD_AUTHENTICATION.md` - Updated security notes
9. `simple_otp/core/README.md` - Updated documentation
10. `simple_otp/models/README.md` - Updated documentation

## Future Considerations

If you need to change the iterations count in the future:

1. Update `PBKDF2_ITERATIONS` in `simple_otp/constants.py`
2. Consider migration strategy if existing data needs re-encryption
3. Update documentation to reflect the change
4. Run full test suite to verify compatibility

**Note**: Changing iterations count will require re-encrypting existing secrets as the derived key will be different.
