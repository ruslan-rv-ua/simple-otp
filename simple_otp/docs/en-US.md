# Simple OTP Help

**Time-based One-Time Password (TOTP) Generator**

*Version: 0.1.0*

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Working with Files](#working-with-files)
4. [Managing Accounts](#managing-accounts)
5. [Generating TOTP Codes](#generating-totp-codes)
6. [Settings](#settings)
7. [Keyboard Shortcuts](#keyboard-shortcuts)
8. [Accessibility](#accessibility)
9. [Security](#security)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

Simple OTP is a secure desktop application for generating Time-based One-Time Passwords (TOTP). It allows you to manage all your two-factor authentication accounts in one place.

### Key Features:

- Generate TOTP codes according to RFC 6238 standard
- Password-based file encryption to protect your secrets
- Support for multiple account files
- Quick account search
- Copy codes to clipboard
- Audio notifications for screen reader users
- Full keyboard navigation support
- Multilingual interface (Ukrainian, English)

## Why?

I, the author, am blind and was looking for a simple and accessible Windows application that would generate TOTP codes and be fully compatible with screen readers.

The community recommended only one widely available option — **KeePass**. While KeePass can store and generate TOTP, it lacked some features that were important specifically for my workflow and accessibility needs.

Having some free time and lots of inspiration, I decided to create Simple OTP. The goal — to make a simple, clear, and convenient tool focused on users who rely on screen readers and keyboard navigation.

If you have ideas or accessibility-related needs, I'd be happy to receive your feedback — it will help make the application better for everyone.

---

## Getting Started

### First Launch

On the first launch of Simple OTP, you'll see an empty application window. To start using the application, you need to:

1. Create a new accounts file (`Ctrl+N`)
2. Set a password to protect your data
3. Add your first account (`F7`)

### System Requirements

- Windows 10 or newer

---

## Working with Files

### Creating a New File

To create a new accounts file:

1. Select **File → New...** or press `Ctrl+N`
2. Choose a save location and enter a filename
3. Set a strong password
4. Confirm the password

> **Important:** Keep your password in a safe place. If you forget the password, recovering access to the file will be impossible!

### Opening an Existing File

To open an existing file:

1. Select **File → Open...** or press `Ctrl+O`
2. Select a file with `.json` extension
3. Enter the password to decrypt the file

### Recent Files

The application stores a list of recent files for quick access. You can:

- Open a recent file through the menu **File → Recent Files**
- Clear the history through **File → Recent Files → Clear History**

---

## Managing Accounts

### Adding an Account

To add a new account:

1. Press `F7` or select **Account → Add**
2. Fill in the required fields:
   - **Name:** account identifier (e.g., user@example.com)
   - **Secret:** Base32 key from the provider (e.g., JBSWY3DPEHPK3PXP)
3. Optionally fill in additional fields:
   - **Issuer:** service name (Google, GitHub, etc.)
   - **Digits:** usually 6 (default)
   - **Algorithm:** usually SHA1 (default)
   - **Period:** usually 30 seconds (default)
4. Press **Add**

### Where to Find the Secret Key

When setting up two-factor authentication, most services show a QR code and a text key. This text key (usually 16-32 characters) is the Base32 secret that needs to be entered into Simple OTP.

### Deleting an Account

To delete an account:

1. Select the account in the list
2. Press `Del` or select **Account → Delete**
3. Confirm deletion

### Searching for Accounts

Use the quick search field in the main window to filter accounts by name or issuer. Search works in real-time as you type.

---

## Generating TOTP Codes

### Getting a Code

To get a TOTP code:

1. Select an account in the list (click with the mouse or use arrow keys)
2. Press `Enter` or double-click
3. A dialog window with the TOTP code will open

### TOTP Dialog Window

The dialog window displays:

- **Current code:** 6-digit code that constantly updates
- **Countdown timer:** time until the next code update
- **Name and issuer:** account information

### Copying the Code

The code is automatically copied to the clipboard when the dialog window opens. You can also:

- Press the **Copy Code** button
- Use the `Ctrl+C` keys

### Automatic Update

The code automatically updates according to the configured period (usually every 30 seconds). An audio signal sounds when updated (if enabled in settings).

---

## Settings

Open the settings window through **Options → Settings...** or press `Ctrl+,`

### "Behavior" Tab

| Setting | Description |
|---------|-------------|
| Auto-close TOTP window | Automatically closes the dialog window after copying the code |
| Play sound on code update | Audio signal when generating a new code |
| Play sound on copy | Audio signal when copying code to clipboard |
| Hide passwords on input | Masks password characters with asterisks (*) |

### "Defaults" Tab

Configure default values for new accounts:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Digits | 6 or 8 | TOTP code length |
| Algorithm | SHA1, SHA256, SHA512 | Hashing algorithm |
| Period | 30 seconds | Code validity time |

### Changing Language

Select the interface language through **Options → Language**. Some interface elements will apply the new language only after restarting the application.

---

## Keyboard Shortcuts

### Main Commands

| Key | Action |
|-----|--------|
| `Ctrl+N` | Create new file |
| `Ctrl+O` | Open file |
| `Ctrl+,` | Open settings |
| `Esc` | Exit application / Close dialog |
| `F7` | Add account |
| `Del` | Delete account |
| `Enter` | Open TOTP code for selected account |

### Navigation

| Key | Action |
|-----|--------|
| `↑` / `↓` | Move through account list |
| `Home` | Go to first account |
| `End` | Go to last account |
| `Tab` | Move between elements |
| `Alt` | Activate menu |

### TOTP Dialog Window

| Key | Action |
|-----|--------|
| `Ctrl+C` | Copy code |
| `Esc` | Close window |

---

## Accessibility

### Screen Reader Support

Simple OTP is fully compatible with screen readers:

- **NVDA** — recommended (free, open-source)
- **JAWS** — full support
- **Windows Narrator** — basic support

### Audio Notifications

The application provides audio signals for important events:

- TOTP code update
- Code copied to clipboard
- Validation errors

Audio signals can be disabled in settings (**Options → Settings → Behavior**).

### Keyboard Navigation

All application features are accessible via keyboard without using a mouse. Use:

- `Tab` to move between elements
- `Enter` or `Space` to activate buttons
- `Alt` + underlined letter for quick menu access
- Arrows to navigate lists and menus

### Braille Display Support

The application is integrated with the VocaBraille library for improved Braille display support. All text elements are correctly displayed in Braille.

### Contrast and Text Sizes

Simple OTP adheres to system settings:

- Uses system fonts and sizes
- Supports Windows high-contrast themes
- Works correctly with DPI settings

---

## Security

### Data Encryption

All account files are encrypted using:

- **AES-256-GCM** — symmetric encryption
- **PBKDF2** — password-based key derivation (600,000 iterations)
- **Random salt** — unique for each file
- **Random nonce** — unique for each encryption operation

### Password Recommendations

For maximum security, use passwords that:

- Contain at least 12 characters (the more, the better)
- Include uppercase and lowercase letters, numbers, and special characters
- Don't contain dictionary words
- Are unique for each file

### Storing Secrets

> **Important:** Base32 secret keys are stored in encrypted form. Never share your account files or secret keys with others!

### Clipboard Security

TOTP codes are copied to the system clipboard. Remember:

- Other applications can read the clipboard contents
- Clear the clipboard after using the code
- Don't leave the code in the clipboard for long

### Backup

Regularly create backups of your account files:

1. Copy `.json` files to a safe place
2. Store backups in encrypted form
3. Use cloud storage with two-factor authentication
4. Store passwords separately from files (use a password manager)

---

## Troubleshooting

### Incorrect Password

**Problem:** "Incorrect password for this file"

**Solution:**

- Make sure you're entering the correct password
- Check keyboard layout (Caps Lock, Num Lock)
- If you've forgotten the password, access recovery is impossible

### Invalid Base32 Secret

**Problem:** "Secret must be a valid Base32 string"

**Solution:**

- Base32 contains only characters A-Z and 2-7
- Remove spaces and hyphens from the secret
- Make sure you've copied the entire secret
- Some services show the secret in a format with spaces — remove them

### Code Doesn't Match

**Problem:** Generated code doesn't work on the website

**Solution:**

- Check the time on your computer — it must be accurate
- Synchronize time through Windows settings
- Make sure parameters (digits, digest, interval) match service requirements
- Usually used: 6 digits, SHA1, 30 seconds

### Screen Reader Problems

**Problem:** Screen reader doesn't read application elements

**Solution:**

- Make sure the screen reader is running before the application
- Try restarting the application
- For NVDA: make sure UIA (UI Automation) support is enabled
- Use keyboard navigation (`Tab`, arrows)

### File Won't Open

**Problem:** "Failed to open file"

**Solution:**

- Check that the file is not corrupted
- Make sure the file is not open in another program
- Check file access permissions
- Try restoring from backup

### Getting Support

If the problem is not resolved:

- Describe the problem in detail (what you did, what you expected, what happened)
- Specify the application version (see **Help → About**)
- Specify Windows version and screen reader (if used)
- Create an issue on GitHub: https://github.com/ruslan-rv-ua/simple-otp

---

## About

**Simple OTP** v0.1.0

© 2025 Ruslan Iskov

**Links:**
- [GitHub](https://github.com/ruslan-rv-ua/simple-otp)
- [Report an Issue](https://github.com/ruslan-rv-ua/simple-otp/issues)

**License:** MIT
