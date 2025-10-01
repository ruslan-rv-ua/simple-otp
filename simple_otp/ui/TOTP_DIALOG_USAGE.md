# TOTP Dialog - Usage Guide

## How to Use

### Opening the TOTP Dialog
1. Launch the Simple OTP application: `uv run python -m simple_otp`
2. In the main window, you'll see a list of accounts
3. To view TOTP codes for an account, either:
   - **Double-click** on an account in the list
   - Select an account and press **Enter**

### TOTP Dialog Features

#### Current Password
- Shows the currently valid one-time password
- Formatted with spaces for readability (e.g., "12 34 56")
- Click **Copy** button to copy the password to clipboard (spaces are removed)
- A confirmation message appears when copied

#### Next Password
- Shows the next one-time password (valid after current interval expires)
- Formatted the same way as current password
- Click **Copy** button to copy to clipboard
- Useful for preparing the next code in advance

#### Progress Bar
- Visual indicator of time remaining in the current interval
- Starts at 100% (full) and decreases to 0%
- When it reaches 0%, the "next" password becomes the "current" password
- Updates smoothly every 100ms

#### Auto-Refresh
- The dialog automatically updates every 100ms
- No need to manually refresh
- Both passwords and progress bar update in real-time

### Keyboard Shortcuts
- **ESC** or **Enter** on Close button - Close the dialog

### Technical Notes
- The dialog uses the same password as configured for the account
- For demo accounts, the password is "demo123"
- Passwords are decrypted on-the-fly when the dialog opens
- The dialog uses PyOTP library for TOTP generation
- Clipboard operations use pyperclip library

## Implementation Details

### Password Formatting
The `format_otp()` function groups digits by 2:
```python
format_otp("123456")   # Returns "12 34 56"
format_otp("12345678") # Returns "12 34 56 78"
```

### Copy Functionality
When copying to clipboard:
1. Spaces are removed from the displayed password
2. Only raw digits are copied (e.g., "123456")
3. pyperclip handles clipboard operations across platforms

### Timer Implementation
- Uses `wx.Timer` for periodic updates
- Update interval: 100ms (10 times per second)
- Timer is properly cleaned up when dialog closes
- Prevents memory leaks and resource issues
