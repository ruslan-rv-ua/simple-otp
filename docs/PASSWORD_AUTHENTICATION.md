# Password Authentication Implementation

## Overview
Implemented a complete password authentication flow for the Simple OTP application with the following features:

## Features Implemented

### 1. Initial Setup Flow
- When no accounts file exists or accounts list is empty:
  - Show dialog requesting password with confirmation
  - Create a default example account encrypted with the entered password
  - Display success message to user

### 2. Login Flow  
- When accounts exist:
  - Show dialog requesting password (no confirmation needed)
  - Attempt to decrypt the first account to verify password
  - Allow up to 3 attempts
  - Show error message with remaining attempts after each failed attempt
  - Close application after 3 failed attempts

### 3. Session Password Management
- Store validated password in MainWindow
- Use stored password for all TOTP operations during session
- No need to re-prompt for password when viewing TOTP codes

## Files Created/Modified

### New Files
1. **simple_otp/ui/password_dialog.py**
   - Custom dialog for password entry
   - Supports optional confirmation field
   - Used for both setup and login flows

### Modified Files
1. **simple_otp/__main__.py**
   - Added `authenticate()` function implementing the authentication flow
   - Handles both first-time setup and existing account login
   - Validates password before showing main window

2. **simple_otp/core/accounts_manager.py**
   - Added `auto_create` parameter to constructor
   - Added `storage_exists()` method
   - Added `has_accounts()` method
   - Added `create_initial_account()` method
   - Added `verify_password()` method

3. **simple_otp/ui/main_window.py**
   - Updated constructor to accept `password` parameter
   - Store password as instance variable
   - Updated `_on_item_activated()` to use stored password

## Usage Flow

### First Time Launch
1. User launches application
2. Password dialog appears: "Welcome to Simple OTP! Please create a master password..."
3. User enters password twice (confirmation required)
4. Default example account is created and encrypted
5. Success message shown
6. Main window opens with account list

### Subsequent Launches
1. User launches application
2. Password dialog appears: "Enter your master password to unlock Simple OTP:"
3. User enters password
4. Password validated by attempting to decrypt first account
5. If incorrect:
   - Show error with remaining attempts (3 total)
   - Prompt again
6. If correct:
   - Main window opens with account list
7. Double-clicking account shows TOTP without re-prompting for password

### Security Notes
- Password is stored in memory for the session
- Used for all decryption operations
- Not persisted to disk
- Application closes after 3 failed login attempts
- All secrets encrypted using AES-256-GCM with PBKDF2-HMAC-SHA256 key derivation
- PBKDF2 iterations set project-wide to 600,000 (OWASP recommendation)
- Iterations constant defined in `simple_otp/constants.py`
