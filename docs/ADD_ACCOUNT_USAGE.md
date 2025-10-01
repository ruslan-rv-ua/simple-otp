# Add Account Feature - Usage Guide

## Overview
The Add Account feature allows users to manually add new TOTP (Time-based One-Time Password) accounts to the Simple OTP application.

## How to Add a New Account

### Opening the Add Account Dialog
You can open the Add Account dialog in two ways:
1. **Menu**: Click `Account` → `Add` in the menu bar
2. **Keyboard Shortcut**: Press `F7`

### Required Fields

#### Name *
- **Description**: The account identifier (e.g., your email address or username)
- **Example**: `user@example.com`, `john.doe`, `myaccount`
- **Required**: Yes

#### Secret (Base32) *
- **Description**: The TOTP secret key in Base32 format
- **Format**: Must be a valid Base32 string (A-Z, 2-7, optional padding with '=')
- **Example**: `JBSWY3DPEHPK3PXP`
- **Notes**: 
  - Spaces are allowed and will be removed automatically
  - Lowercase letters will be converted to uppercase
  - Must be at least 8 characters long
- **Required**: Yes

### Optional Fields

#### Issuer
- **Description**: The service or organization providing the OTP (e.g., Google, GitHub, AWS)
- **Example**: `Google`, `GitHub`, `Amazon AWS`
- **Default**: Empty string
- **Display**: If provided, accounts are displayed as "Issuer (Name)"

#### Digits
- **Description**: Number of digits in the generated OTP code
- **Options**: 6 or 8
- **Default**: 6
- **Note**: Most services use 6 digits

#### Digest Algorithm
- **Description**: Hash algorithm used for TOTP generation
- **Options**: 
  - SHA1 (most common)
  - SHA256
  - SHA512
- **Default**: SHA1
- **Note**: Most services use SHA1

#### Interval (seconds)
- **Description**: Time interval for code generation
- **Range**: 1-300 seconds
- **Default**: 30 seconds
- **Note**: Most services use 30 seconds

## Validation

The dialog performs the following validations:

1. **Name**: Cannot be empty
2. **Secret**: 
   - Cannot be empty
   - Must be valid Base32 format
   - Must be decodable (valid Base32 data)
3. **Duplicate Check**: Account with same name and issuer cannot exist

## Examples

### Example 1: Basic Account (Google)
- **Name**: `user@gmail.com`
- **Secret**: `JBSWY3DPEHPK3PXP`
- **Issuer**: `Google`
- **Other fields**: Use defaults
- **Display Name**: `Google (user@gmail.com)`

### Example 2: GitHub Account with Custom Settings
- **Name**: `myusername`
- **Secret**: `ABCD EFGH IJKL MNOP`
- **Issuer**: `GitHub`
- **Digits**: 8
- **Digest**: SHA256
- **Interval**: 60
- **Display Name**: `GitHub (myusername)`

### Example 3: Simple Account Without Issuer
- **Name**: `test@example.com`
- **Secret**: `JBSWY3DPEHPK3PXP`
- **Issuer**: (leave empty)
- **Other fields**: Use defaults
- **Display Name**: `test@example.com`

## Common Issues

### "Secret must be a valid Base32 string"
- **Cause**: Secret contains invalid characters
- **Solution**: Ensure secret only contains A-Z, 2-7, and optional '=' for padding
- **Note**: Base32 does not use 0, 1, 8, or 9

### "Invalid Base32 secret"
- **Cause**: Secret cannot be decoded
- **Solution**: Double-check the secret from your service provider
- **Tip**: Copy-paste the secret to avoid typos

### "Account already exists"
- **Cause**: An account with the same name and issuer already exists
- **Solution**: 
  - Use a different name or issuer
  - Delete the existing account first
  - Edit the name to make it unique (e.g., add a suffix)

## Security Notes

1. **Password Protection**: The secret is encrypted using your master password before being saved
2. **Secure Storage**: Secrets are stored encrypted in the `accounts.json` file
3. **No Plaintext**: Secrets are never stored in plaintext
4. **Key Derivation**: PBKDF2-HMAC-SHA256 with 600,000 iterations is used for key derivation

## Tips

1. **Test First**: After adding an account, immediately test it by opening the TOTP dialog
2. **Keep Backup**: Keep a backup of your secrets in a secure location
3. **Group by Issuer**: Use consistent issuer names to group related accounts
4. **Descriptive Names**: Use descriptive names that help you identify the account quickly

## Keyboard Shortcuts

- **F7**: Open Add Account dialog
- **Enter**: Submit the form (when all fields are valid)
- **Esc**: Cancel and close the dialog
