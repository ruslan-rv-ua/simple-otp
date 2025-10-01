"""Example usage of TOTPAccount model with encryption."""

from simple_otp.models import DigestAlgorithm, Encryptor, TOTPAccount


# Example 1: Create a new TOTP account with default settings
def example_create_default_account():
    """Example: Create account with default settings (6 digits, SHA1, 30s interval)."""
    # User's plain TOTP secret (typically from QR code)
    plain_secret = "JBSWY3DPEHPK3PXP"
    user_password = "my_secure_password_123"

    # Generate salt and encrypt the secret using Encryptor
    salt = Encryptor.generate_salt()
    encrypted_secret = Encryptor.encrypt(plain_secret, user_password, salt)

    # Create TOTP account
    account = TOTPAccount(
        encrypted_secret=encrypted_secret,
        salt=salt,
        name="user@example.com",
        issuer="GitHub",
    )

    print(f"Created account: {account.get_display_name()}")
    print(f"Digits: {account.digits}, Interval: {account.interval}s")
    return account, user_password


# Example 2: Create account with custom settings
def example_create_custom_account():
    """Example: Create account with 8 digits, SHA256, and 60s interval."""
    plain_secret = "JBSWY3DPEHPK3PXP"
    user_password = "my_secure_password_123"

    # Generate salt and encrypt the secret
    salt = Encryptor.generate_salt()
    encrypted_secret = Encryptor.encrypt(plain_secret, user_password, salt)

    # Create account with custom parameters
    account = TOTPAccount(
        encrypted_secret=encrypted_secret,
        salt=salt,
        name="admin@company.com",
        issuer="AWS",
        digits=8,
        digest=DigestAlgorithm.SHA256,
        interval=60,
    )

    print(f"Created account: {account.get_display_name()}")
    print(
        f"Digits: {account.digits}, Digest: {account.digest}, Interval: {account.interval}s"
    )
    return account, user_password


# Example 3: Generate TOTP code using the new get_totp() method
def example_generate_totp_code(account: TOTPAccount, user_password: str):
    """Example: Generate TOTP code using account's get_totp() method."""
    # Get PyOTP TOTP instance (automatically decrypts secret)
    totp = account.get_totp(user_password)

    # Generate current code
    code = totp.now()
    print(f"Current TOTP code for {account.get_display_name()}: {code}")

    # You can also verify codes
    is_valid = totp.verify(code)
    print(f"Code verification: {is_valid}")

    return code


# Example 4: Direct decryption if needed
def example_decrypt_secret():
    """Example: Directly decrypt a secret using Encryptor."""
    plain_secret = "JBSWY3DPEHPK3PXP"
    password = "test_password"

    # Encrypt
    salt = Encryptor.generate_salt()
    encrypted = Encryptor.encrypt(plain_secret, password, salt)
    print(f"Encrypted secret: {encrypted}")

    # Decrypt
    decrypted = Encryptor.decrypt(encrypted, password, salt)
    print(f"Decrypted secret: {decrypted}")
    print(f"Match: {plain_secret == decrypted}")

    return decrypted


if __name__ == "__main__":
    # Run examples
    print("=" * 60)
    print("Example 1: Default account (6 digits, SHA1, 30s)")
    print("=" * 60)
    account1, password1 = example_create_default_account()
    example_generate_totp_code(account1, password1)

    print("\n" + "=" * 60)
    print("Example 2: Custom account (8 digits, SHA256, 60s)")
    print("=" * 60)
    account2, password2 = example_create_custom_account()
    example_generate_totp_code(account2, password2)

    print("\n" + "=" * 60)
    print("Example 3: Direct encryption/decryption")
    print("=" * 60)
    example_decrypt_secret()
