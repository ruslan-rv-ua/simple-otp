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
- Audio notifications
- Full keyboard navigation support

## Why?

I'm a blind developer who was looking for the perfect TOTP code generation app for Windows — simple, accessible, and fully screen reader compatible.

The community suggested only one option — **KeePass**. It handles TOTP storage and generation, but lacked those features that were vital for my workflow and accessibility needs.

So, with some time and lots of inspiration, I created **Simple OTP**. My goal is to create a simple, clear, and convenient tool for those who rely on screen readers and keyboard navigation.

If you have ideas, I'd be happy to receive your feedback — it will help make the application better for everyone.

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

After creating the file, the application will automatically create a test account to verify TOTP functionality:

- **Name**: `totp@authenticationtest.com`
- **Issuer**: `AuthenticationTest.com`

You can use this account for testing at [authenticationtest.com](https://authenticationtest.com/totpChallenge). After verification, it can be deleted.

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
   - **Issuer:** service name (Google, GitHub, Binance, etc.)
   - **Digits:** usually 6, but 7 and 8 are also supported
   - **Hash algorithm:** usually SHA1, SHA256 and SHA512 are also available
   - **Period:** usually 30 seconds
4. Press **OK**

### Where to Find the Secret Key

When setting up two-factor authentication, most services show a QR code and a text key. This text key (usually 16-32 characters) is the Base32 secret that needs to be entered into Simple OTP.

### Deleting an Account

To delete an account:

1. Select the account in the list
2. Press `Del` or select **Account → Delete**
3. Confirm deletion

### Searching for Accounts

Use the quick search field in the main window to filter accounts by name or issuer. Search activates after entering at least 3 characters and works in real-time. Search is performed for all words entered separated by spaces.

---

## Generating TOTP Codes

### Getting a Code

To get a TOTP code:

1. Select an account in the list (click with the mouse or use arrow keys)
2. Press `Enter` or double-click
3. A dialog window with the TOTP code will open

### TOTP Dialog Window

The dialog window displays:

- **Current code:** valid TOTP code that can be used right now for authentication (formatted with spaces, e.g., "12 34 56")
- **Next code:** TOTP code that will become valid after the current code expires
- **Remaining time progress:** indicator showing how much time is left until automatic code update

### Copying the Code

The current code is **automatically copied** to the clipboard when the dialog window opens. You can also:

- Press the **Copy Current** or **Copy Next** button
- Use hotkeys `K` (current) or `D` (next)
- Use combinations `Ctrl+Enter` (current) or `Ctrl+Shift+Enter` (next)

An audio signal sounds when copying (if enabled in settings).

### Automatic Update

The code automatically updates according to the configured period (usually every 30 seconds). When updating:
- An audio signal sounds (if enabled)
- The code can be automatically copied to the clipboard (if configured)
- The code can be automatically spoken by the screen reader (if configured)
- A few seconds before expiration, a warning signal may sound (if configured)

---

## Settings

Open the settings window through **Options → Settings...** or press `Ctrl+,`

### "Behavior" Tab

| Setting | Description |
|---------|-------------|
| Automatically copy password to clipboard on update | New code is automatically copied on each update |
| Hide passwords in TOTP dialog | Displays codes as '******' and disables keyboard focusing |
| Automatically speak password on update | New code is automatically spoken by screen reader on update |
| Open last file on startup | Automatically opens the last used file when starting the application |

### "Audio" Tab

| Setting | Description |
|---------|-------------|
| Play sound when copying current password | Audio signal when copying current code |
| Play sound when copying next password | Audio signal when copying next code |
| Play sound on password update | Audio signal when generating a new code |
| Play warning sound | Audio signal before password expiration |
| Play warning sound (seconds before expiration) | Number of seconds before expiration when warning starts (default 5) |

### "TOTP Defaults" Tab

Configure default values for new accounts:

| Parameter | Value | Description |
|-----------|-------|-------------|
| Digits | 6, 7, or 8 | TOTP code length (default 6) |
| Algorithm | SHA1, SHA256, SHA512 | Hashing algorithm (default SHA1) |
| Period | 15-120 seconds | Code validity time (default 30) |

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
| `K` | Copy current code |
| `D` | Copy next code |
| `J` or `Enter` | Speak current code (by screen reader) |
| `F` or `Shift+Enter` | Speak next code (by screen reader) |
| `Ctrl+Enter` | Copy current code |
| `Ctrl+Shift+Enter` | Copy next code |
| `A` or `Esc` | Close window |

---

## Accessibility

### Screen Reader Support

Simple OTP has been tested with the NVDA screen reader. Theoretically, the application is compatible with any screen reader.

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

---

## Security

### Data Encryption

All account files are encrypted using:

- **AES-256-GCM** — symmetric encryption with built-in authentication
- **PBKDF2-HMAC-SHA256** — password-based key derivation (600,000 iterations according to OWASP 2023 recommendations)
- **Random salt** — unique for each file (generated by the `secrets` module)
- **Random nonce** — unique for each encryption operation

### Password Recommendations

For maximum security, use passwords that:

- Contain at least 12 characters (the more, the better)
- Include uppercase and lowercase letters, numbers, and special characters
- Don't contain dictionary words
- Are unique for each file

### Storing Secrets

> **Important:** Base32 secret keys are stored in encrypted form. Never share your secret keys with others!

### Clipboard Security

TOTP codes are copied to the system clipboard. Remember:

- Other applications can read the clipboard contents
- Codes are copied without spaces (even if displayed with formatting)

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

- Base32 contains only characters A-Z and 2-7, optionally with '=' characters for alignment
- Remove spaces and hyphens from the secret (the application does this automatically, but it's better to enter clean text)
- Make sure you've copied the entire secret
- Some services show the secret in a format with spaces — the application automatically removes them during validation

### Code Doesn't Match

**Problem:** Generated code doesn't work on the website

**Solution:**

- Check the time on your computer — it must be accurate (synchronized with an internet server)
- Synchronize time through Windows settings (Settings → Time & Language → Time Synchronization)
- Make sure parameters (digits, digest, interval) match service requirements
- Usually used: 6 digits, SHA1, 30 seconds
- When entering the code on a website, enter WITHOUT spaces (123456, not 12 34 56)

### File Won't Open

**Problem:** "Failed to open file"

**Solution:**

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
