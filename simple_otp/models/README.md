# Models Package

This package contains the data models for the simple-otp application.

## TOTPAccount

The `TOTPAccount` dataclass represents a TOTP (Time-based One-Time Password) account with encrypted secret storage.

### Features

- **Encrypted Secret Storage**: Secrets are encrypted using AES-256-GCM with password-based key derivation (PBKDF2-HMAC-SHA256)
- **Base64 Encoding**: All sensitive data is stored as base64-encoded strings for easy serialization
- **PyOTP Integration**: Direct integration with PyOTP library via `get_totp()` method
- **Flexible Configuration**: Support for 6 or 8 digit codes, SHA1/SHA256/SHA512 algorithms, custom intervals

### Usage

```python
from simple_otp.models import TOTPAccount, DigestAlgorithm, Encryptor

# 1. Generate salt and encrypt secret
plain_secret = "JBSWY3DPEHPK3PXP"  # Base32-encoded secret from QR code
password = "user_password"
salt = Encryptor.generate_salt()
encrypted_secret = Encryptor.encrypt(plain_secret, password, salt)

# 2. Create TOTP account
account = TOTPAccount(
    encrypted_secret=encrypted_secret,
    salt=salt,
    name="user@example.com",  # REQUIRED
    issuer="GitHub",           # Optional
    digits=6,                  # Optional: 6 or 8
    digest=DigestAlgorithm.SHA1,  # Optional: SHA1, SHA256, SHA512
    interval=30                # Optional: seconds
)

# 3. Generate TOTP codes
totp = account.get_totp(password)
code = totp.now()  # Current 6-digit code
print(f"Code: {code}")

# 4. Verify codes
is_valid = totp.verify(code, valid_window=1)
```

### Fields

#### Required Fields
- `encrypted_secret` (str): Base64-encoded encrypted TOTP secret
- `salt` (str): Base64-encoded cryptographic salt (16+ bytes)
- `name` (str): Account identifier (email, username, etc.) - **REQUIRED**

#### Optional Fields
- `issuer` (str): Service name (e.g., "Google", "GitHub")
- `digits` (int): Code length - 6 or 8 (default: 6)
- `digest` (DigestAlgorithm): Hash algorithm (default: SHA1)
- `interval` (int): Time step in seconds (default: 30)

**Note**: PBKDF2 iterations are now defined project-wide in `simple_otp/constants.py` (600,000 iterations). The `iterations` field has been removed from the dataclass.

### Methods

#### `get_display_name() -> str`
Returns a user-friendly display name:
- If both issuer and name: `"GitHub (user@example.com)"`
- If only issuer: `"GitHub"`
- If only name: `"user@example.com"`

#### `get_totp(password: str) -> pyotp.TOTP`
Decrypts the secret and returns a configured PyOTP TOTP instance.

**Parameters:**
- `password`: User's password for decryption

**Returns:**
- `pyotp.TOTP` instance ready to generate/verify codes

**Raises:**
- `cryptography.exceptions.InvalidTag`: If password is incorrect

## Encryptor

Helper class for encrypting and decrypting TOTP secrets.

### Methods

#### `generate_salt() -> str`
Generates a cryptographically secure 16-byte salt (base64-encoded).

#### `encrypt(plain_secret: str, password: str, salt: str) -> str`
Encrypts a plain text secret using password-based encryption.

**Parameters:**
- `plain_secret`: Plain TOTP secret (base32 string)
- `password`: Encryption password
- `salt`: Base64-encoded salt

**Returns:**
- Base64-encoded encrypted secret

**Note:**
- Uses `PBKDF2_ITERATIONS` constant (600,000) from `simple_otp.constants`

#### `decrypt(encrypted_secret: str, password: str, salt: str) -> str`
Decrypts an encrypted secret.

**Parameters:**
- `encrypted_secret`: Base64-encoded encrypted secret
- `password`: Decryption password
- `salt`: Base64-encoded salt (same as used for encryption)

**Returns:**
- Decrypted plain text secret

**Raises:**
- `cryptography.exceptions.InvalidTag`: If password is incorrect or data is corrupted

**Note:**
- Uses `PBKDF2_ITERATIONS` constant (600,000) from `simple_otp.constants`

## DigestAlgorithm

String enum for supported TOTP digest algorithms.

### Values
- `SHA1`: Most common (default for most services)
- `SHA256`: Higher security
- `SHA512`: Highest security

### Methods

#### `get_digest() -> Any`
Returns the corresponding hashlib digest function (`sha1`, `sha256`, or `sha512`).

## Security Notes

1. **Salt Generation**: Always use `Encryptor.generate_salt()` for cryptographically secure salts
2. **Iterations**: Project-wide constant of 600,000 iterations (defined in `simple_otp/constants.py`) follows OWASP recommendations for PBKDF2-HMAC-SHA256
3. **Password Storage**: Never store passwords - only use them for encryption/decryption operations
4. **Secret Protection**: Keep encrypted secrets and salts secure; compromise of both with password allows secret recovery
5. **Consistency**: All accounts use the same iteration count for encryption, ensuring consistent security across the application

## Examples

See `example_usage.py` for complete working examples including:
- Creating accounts with default settings
- Creating accounts with custom parameters (8 digits, SHA256, 60s interval)
- Generating and verifying TOTP codes
- Direct encryption/decryption operations
