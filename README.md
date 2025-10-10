# Simple OTP

Desktop application for generating TOTP (Time-based One-Time Passwords) using wxPython GUI.

## Features

- **TOTP Code Generation**: Generate 6 or 8-digit time-based one-time passwords
- **Encrypted Storage**: All secrets are encrypted using PBKDF2-HMAC-SHA256 (600,000 iterations, project-wide constant)
- **Multiple Accounts**: Manage multiple TOTP accounts with search functionality
- **Real-time Display**: View current and next codes with countdown timer
- **Password Protection**: Master password protects all stored secrets
- **Add/Edit/Delete**: Full account management capabilities

## Installation

This project uses `uv` for dependency management. Make sure you have `uv` installed.

```cmd
REM Clone the repository
git clone <repository-url>
cd simple-otp

REM Install dependencies
uv sync

REM Run the application
uv run python -m simple_otp
```

## First Run and Testing

On first run, the application creates a default test account that you can use to verify the TOTP implementation works correctly.

### Default Test Account

The application includes a default test account from [authenticationtest.com](https://authenticationtest.com/totpChallenge):

- **Email**: `totp@authenticationtest.com`
- **Secret**: `I65VU7K5ZQL7WB4E`
- **Issuer**: `AuthenticationTest.com`
- **Master Password**: `example_password` (for initial storage)

### How to Test the Default Account

1. **Run the application**:
   ```cmd
   uv run python -m simple_otp
   ```

2. **Enter the master password**: `example_password`

3. **Open the default account**: Double-click on `AuthenticationTest.com (totp@authenticationtest.com)` or press Enter

4. **Verify the code**: 
   - Copy the current TOTP code from the dialog
   - Visit https://authenticationtest.com/totpChallenge
   - Enter the credentials:
     - **Email**: `totp@authenticationtest.com`
     - **Password**: `pa$$w0rd`
     - **MFA Code**: Paste the TOTP code you copied
   - Click "Log In"

5. **Success!** If the code is valid and within the time window, you should successfully authenticate, confirming that Simple OTP is generating correct TOTP codes.

### Important Notes

- The test account is publicly available and should only be used for verification purposes
- For production use, delete the test account and add your own accounts
- Always use a strong master password for your own accounts

## Usage

### Adding a New Account

1. Press **F7** or click **Account** → **Add**
2. Enter the required information:
   - **Name**: Account identifier (e.g., email or username)
   - **Secret**: Base32-encoded TOTP secret key
   - **Issuer** (optional): Service name (e.g., Google, GitHub)
   - **Digits** (optional): 6 or 8 digits (default: 6)
   - **Digest** (optional): SHA1, SHA256, or SHA512 (default: SHA1)
   - **Interval** (optional): Time interval in seconds (default: 30)
3. Click **Add**

See [docs/ADD_ACCOUNT_USAGE.md](docs/ADD_ACCOUNT_USAGE.md) for detailed instructions.

### Viewing TOTP Codes

1. **Double-click** an account in the list or select it and press **Enter**
2. The TOTP dialog shows:
   - **Current code**: Currently valid OTP
   - **Next code**: OTP for the next time interval
   - **Progress bar**: Time remaining in current interval
   - **Copy buttons**: Copy codes to clipboard
3. Codes update automatically every 100ms

### Searching Accounts

- Type at least **3 characters** in the search box
- Searches both account name and issuer
- Supports multi-word search (all words must match)

### Deleting an Account

1. Select an account in the list
2. Press **Del** or click **Account** → **Delete**
3. Confirm the deletion

## Keyboard Shortcuts

- **F7**: Add new account
- **Del**: Delete selected account
- **Esc**: Exit application
- **Enter**: Open selected account / Submit dialog
- **Ctrl+F**: Focus search box (when implemented)

## Technology Stack

- **Python**: 3.13+
- **GUI Framework**: wxPython 4.2.3+
- **List Control**: ObjectListView3 1.3.5+
- **OTP Library**: PyOTP 2.9.0+
- **Encryption**: cryptography 46.0.2+
- **Package Manager**: uv

## Security

- **Encryption**: All TOTP secrets are encrypted using AES-256-GCM
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP recommended)
- **Salt**: Unique cryptographic salt per account (16 bytes)
- **No Plaintext**: Secrets are never stored in plaintext
- **Memory Safety**: Secrets are only decrypted when needed

## Architecture (v0.6.0+)

Starting from v0.6.0, the application follows a cleaner architecture with better separation of concerns:

- **Entry Point (`__main__.py`)**: Minimal initialization - creates wx.App, initializes i18n, and launches MainWindow
- **MainWindow**: Owns all file operations and authentication logic
  - `_authenticate()`: Centralized authentication for all file operations
  - `_open_last_file_on_startup()`: Handles automatic file opening on startup (configurable in settings)
  - Manages accounts file lifecycle (create, open, switch)
- **No Duplication**: Single authentication flow used for startup, file opening, and recent files

This design improves testability, maintainability, and follows SOLID principles.

## Project Structure

```
simple-otp/
├── pyproject.toml          # Project metadata and dependencies
├── README.md               # This file
├── uv.lock                 # Dependency lock file
├── docs/                   # Documentation
│   ├── ADD_ACCOUNT_USAGE.md
│   └── PASSWORD_AUTHENTICATION.md
├── simple_otp/             # Main package
│   ├── __init__.py
│   ├── __main__.py         # Entry point (minimal launcher)
│   ├── core/               # Business logic
│   │   ├── accounts_manager.py
│   │   ├── encryptor.py
│   │   ├── i18n.py
│   │   └── settings_manager.py
│   ├── models/             # Data models
│   │   └── totp_account.py
│   └── ui/                 # GUI components
│       ├── main_window.py  # Main application window (owns file logic)
│       ├── add_account_dialog.py
│       ├── password_dialog.py
│       ├── settings_dialog.py
│       └── totp_dialog.py
└── tests/                  # Unit tests
    ├── test_accounts_manager.py
    ├── test_add_account_dialog.py
    ├── test_main_window.py
    ├── test_settings_dialog.py
    └── test_totp_account.py
```

## Development

### Running Tests

```cmd
REM Run all tests
uv run pytest

REM Run specific test file
uv run pytest tests/test_add_account_dialog.py

REM Run with verbose output
uv run pytest -v
```

### Adding Dependencies

```cmd
REM Add a new dependency
uv add <package-name>

REM Add a development dependency
uv add --dev <package-name>
```

## Contributing

1. Follow **Conventional Commits** format:
   - `feat(scope): description` - New features
   - `fix(scope): description` - Bug fixes
   - `docs(scope): description` - Documentation
   - `refactor(scope): description` - Code refactoring
   - `test(scope): description` - Tests

2. Ensure all tests pass before committing
3. Use `uv` for all dependency management
4. Keep security best practices in mind

## License

[Add your license information here]

## Credits

- Default test account provided by [AuthenticationTest.com](https://authenticationtest.com/)
- TOTP implementation based on [RFC 6238](https://tools.ietf.org/html/rfc6238)
- Uses [PyOTP](https://github.com/pyauth/pyotp) for TOTP generation

## Support

[Add support information here]
