# Logging Implementation Documentation

## Overview

The Simple OTP application uses **loguru** for comprehensive logging. All application events, errors, and user actions are logged to a file for debugging and troubleshooting purposes.

## Configuration

### Log File Location

The log file is located at the root of the project:
```
simple-otp/
├── simple_otp.log     # ← Log file (recreated on each app start)
├── simple_otp/
│   └── ...
```

### Logging Configuration

Logging is configured in `simple_otp/core/logger.py`:

- **Log Level**: `DEBUG` - detailed logging for all operations
- **File Mode**: `w` (write) - file is recreated on each application start, **previous content is lost**
- **Format**: `{time} | {level} | {name}:{function}:{line} - {message}`
- **Backtrace**: Enabled - full call stack in exceptions
- **Diagnose**: Enabled - variable values shown in tracebacks
- **Encoding**: UTF-8
- **Output**: File only (no terminal/console output)
- **Language**: English only (no localization)

Example log entry:
```
2025-10-10 15:30:45.123 | INFO     | simple_otp.__main__:main:12 - Starting Simple OTP application
```

## Accessing the Log File

Users can open the log file from the application menu:

**Options → Open Log File**

This menu item:
- Opens the log file in the system's default text editor
- Works on Windows using `os.startfile()`
- Shows an error message if the log file doesn't exist or cannot be opened
- Is available in both English and Ukrainian locales

### Menu Shortcuts
- English: `Options → Open Log File`
- Ukrainian: `Опції → Відкрити лог-файл`

## What Is Logged

### Application Lifecycle
- Application startup and initialization
- Main window creation
- Settings loading
- Locale detection and configuration
- Application shutdown

### File Operations
- Creating new accounts files
- Opening existing files
- File loading and parsing
- File saving
- Recent files management
- Storage path resolution

### Account Management
- Adding new accounts (with account name and issuer)
- Deleting accounts (with confirmation)
- Loading accounts from storage
- Saving accounts to storage
- Account validation errors
- Duplicate account detection

### User Interface Events
- Menu selections
- Dialog openings and closures
- List item activations
- Search operations
- Language changes
- Settings modifications

### Authentication
- Password dialog displays
- Password verification attempts
- Authentication success/failure
- Password-related errors

### TOTP Operations
- TOTP dialog openings
- TOTP code generation requests
- Clipboard operations
- Timer events

### Errors and Exceptions
All exceptions are logged with:
- Full traceback (backtrace enabled)
- Variable values at each frame (diagnose enabled)
- Exception type and message
- Context information (which operation failed, what parameters were used)

Example exception log:
```
2025-10-10 15:35:12.456 | ERROR    | simple_otp.ui.main_window:_on_add_account:420 - Failed to add account (ValueError): Account with name 'test@example.com' and issuer 'Google' already exists
Traceback (most recent call last):
  File "c:\dev\simple-otp\simple_otp\ui\main_window.py", line 404, in _on_add_account
    self.accounts_manager.add_account(new_account)
    │                      │           └ <TOTPAccount(name='test@example.com', issuer='Google')>
    │                      └ <AccountsManager at 0x...>
    └ <MainWindow at 0x...>
ValueError: Account with name 'test@example.com' and issuer 'Google' already exists
```

## Logging Best Practices

### Log Levels Used

- **DEBUG**: Detailed information for diagnosing issues
  - UI component creation
  - Method entry/exit
  - Variable state
  - Internal operations

- **INFO**: General informational messages
  - User actions
  - File operations
  - Successful operations
  - State changes

- **WARNING**: Potentially problematic situations
  - Operation attempted with no file open
  - No account selected for operation
  - Non-critical validation issues

- **ERROR**: Error events that might still allow the application to continue
  - Failed to add/delete account
  - File operation errors
  - Validation failures
  - Expected exceptions

- **CRITICAL**: Severe errors that might cause application termination
  - Fatal initialization errors
  - Unrecoverable exceptions in main()

### Exception Logging

Exceptions are logged using `logger.opt(exception=True)`:

```python
try:
    risky_operation()
except Exception as e:
    logger.opt(exception=True).error(f"Operation failed: {e}")
    # Re-raise or handle appropriately
```

This automatically includes:
- Full traceback with variable values
- Exception type and message
- Call stack context

## Key Modules with Logging

### `simple_otp/__main__.py`
- Application startup and initialization
- Settings and locale configuration
- Main loop lifecycle
- Top-level exception handling

### `simple_otp/ui/main_window.py`
- Main window initialization
- Menu event handlers
- Account operations (add, delete, view)
- File operations (new, open)
- User interactions
- Dialog management

### `simple_otp/core/accounts_manager.py`
- Account loading from JSON
- Account saving to JSON
- Account add/delete operations
- Storage file management
- JSON parsing errors

### `simple_otp/core/logger.py`
- Logging configuration
- Log file path management
- Convenience functions for exception logging

## Implementation Details

### Initialization

Logging is initialized as the first operation in `main()`:

```python
def main():
    # Initialize logging first to capture all application events
    configure_logging()
    logger.info("Starting Simple OTP application")
    # ... rest of initialization
```

### Error Handling Pattern

All critical operations use try-except with logging:

```python
try:
    logger.debug("Starting operation X")
    perform_operation()
    logger.info("Operation X completed successfully")
except SpecificException as e:
    logger.opt(exception=True).error(f"Operation X failed: {e}")
    # Show user-friendly error message
    raise
```

### User Action Logging

User actions are logged at INFO level:

```python
def _on_add_account(self, event):
    logger.debug("Add account menu item clicked")
    # ... validation ...
    logger.info(f"User confirmed adding account: {name} ({issuer})")
    # ... perform operation ...
```

## Performance Considerations

- **Enqueue**: Enabled - logging is done in a background thread to avoid blocking the UI
- **File Rotation**: Not enabled - file is recreated on each start
- **Compression**: Not enabled - log files are human-readable
- **Retention**: Not applicable - only current session log is kept

## Security Notes

1. **Passwords are NEVER logged** - only success/failure of authentication
2. **TOTP codes are NEVER logged** - only dialog open/close events
3. **Encrypted secrets are NEVER logged** - only account names and issuers
4. **File paths are logged** - to aid in troubleshooting file operations
5. **Logs are in English only** - consistent format regardless of UI language

## Troubleshooting

### Log File Not Found

If the log file doesn't exist when "Open Log File" is selected:
- The log file is created only after the first log entry
- Close and restart the application to create the log file
- Check file system permissions in the project directory

### Log File Empty

The log file is recreated on each application start:
- Previous logs are not preserved
- If you need to keep logs, copy the file before restarting
- Consider implementing log rotation if historical logs are needed

### Log File Cannot Be Opened

Possible causes:
- File system permissions issues
- Log file is locked by another process
- No default text editor configured in Windows
- File path contains special characters

## Future Enhancements

Potential improvements to the logging system:

1. **Log Rotation**: Keep multiple log files with timestamps
2. **Compression**: Compress old log files to save space
3. **Retention Policy**: Automatically delete logs older than X days
4. **Log Level Configuration**: Allow users to choose log verbosity
5. **Export Logs**: Button to save logs to a different location
6. **Filter Logs**: View only errors or warnings in the UI
7. **Real-time Log Viewer**: Show logs in a separate window

## Related Files

- `simple_otp/core/logger.py` - Main logging configuration
- `simple_otp/__main__.py` - Logging initialization
- `simple_otp/ui/main_window.py` - Menu item for opening log file
- `simple_otp/locales/en-US.json` - English menu labels and messages
- `simple_otp/locales/uk-UA.json` - Ukrainian menu labels and messages
- `simple_otp.log` - The actual log file (generated at runtime)

## References

- **loguru documentation**: https://github.com/delgan/loguru
- **loguru API reference**: https://loguru.readthedocs.io/
- **Best practices**: Use DEBUG for development, INFO for production
