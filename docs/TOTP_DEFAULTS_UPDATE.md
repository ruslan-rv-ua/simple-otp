# TOTP Defaults Implementation - Change Summary

## Overview

This update implements TOTP Defaults settings functionality and removes unused placeholder settings from the application.

## Changes Made

### 1. Settings Manager (`simple_otp/core/settings_manager.py`)

**Removed:**
- UI settings (`theme`, `font_size`) - no functionality implemented
- Security settings (`auto_copy`, `clear_clipboard`, `clipboard_timeout`) - no functionality implemented

**Retained:**
- TOTP defaults (`default_digits`, `default_interval`, `default_digest`)
- Behavior settings (`auto_copy_on_update`)
- Audio settings (`play_password_copied_sound`, `play_warning_sound`, `warning_sound_seconds`)

### 2. Settings File (`simple_otp/settings.json`)

Updated to reflect only implemented settings:

```json
{
  "version": "1.0",
  "totp": {
    "default_digits": 6,
    "default_interval": 30,
    "default_digest": "SHA1"
  },
  "behavior": {
    "auto_copy_on_update": false
  },
  "audio": {
    "play_password_copied_sound": true,
    "play_warning_sound": true,
    "warning_sound_seconds": 5
  }
}
```

### 3. Settings Dialog (`simple_otp/ui/settings_dialog.py`)

**Removed:**
- "User Interface" page (no functionality)
- "Security" page (no functionality)

**Updated:**
- Created new "Behavior" page for application behavior settings
- Moved `auto_copy_on_update` checkbox from Audio to Behavior page (more appropriate)
- Enabled all TOTP Defaults controls (previously disabled placeholders)
- Now has 3 pages: "TOTP Defaults", "Behavior", and "Audio"

### 4. Add Account Dialog (`simple_otp/ui/add_account_dialog.py`)

**Enhanced:**
- Now accepts `settings_manager` parameter
- Automatically loads TOTP defaults from settings
- Pre-fills digits, interval, and digest fields with user's preferred defaults
- Added support for 7-digit codes (choices are now 6, 7, 8)

**Example:**
If user has set defaults to 8 digits, 60 seconds, SHA256, these values will be automatically selected when opening the Add Account dialog.

### 5. Main Window (`simple_otp/ui/main_window.py`)

**Updated:**
- Passes `settings_manager` to `AddAccountDialog` when creating new accounts

### 6. Tests

**Updated all test files:**
- `test_add_account_dialog.py` - Updated to use settings_manager fixture
- `test_settings_manager.py` - Removed tests for deleted settings
- `test_settings_dialog.py` - Updated to test only implemented pages

**Test Results:** ✅ All 129 tests pass

### 7. Documentation

**Updated `docs/SETTINGS.md`:**
- Removed references to unimplemented settings
- Updated structure to show only TOTP and Audio settings
- Marked TOTP Defaults and Audio Settings as "Fully Implemented"
- Updated code examples to use actual settings

## User Benefits

1. **Convenient Defaults**: Users can set their preferred TOTP parameters once, and they'll be automatically used for new accounts
2. **Less Clutter**: Settings dialog only shows functional settings, avoiding confusion
3. **Better Organization**: Auto-copy setting moved to Audio page where it makes more sense
4. **More Flexibility**: Support for 7-digit TOTP codes added

## Technical Benefits

1. **Cleaner Codebase**: Removed non-functional placeholder code
2. **Better Testing**: Tests now focus on actual functionality
3. **Accurate Documentation**: Docs reflect actual implementation
4. **Future-Ready**: Easy to add new settings when functionality is implemented

## Migration Notes

Existing `settings.json` files will automatically merge with new defaults:
- Old UI and Security settings will be ignored
- TOTP and Audio settings will be preserved
- Missing settings will be filled with defaults

## Usage Example

```python
# User sets preferred defaults in Settings dialog:
# - Digits: 8
# - Interval: 60
# - Digest: SHA256

# When adding a new account:
# 1. User opens Add Account dialog (F7 or Account menu)
# 2. Dialog automatically shows 8 digits, 60s interval, SHA256
# 3. User can still change these for this specific account
# 4. Enter name and secret, click Add
```

## Commit Information

Feature branch: `feature/app-settings`

Changes:
- Implemented TOTP defaults in Add Account dialog
- Removed unimplemented UI and Security settings
- Updated Settings dialog to show only functional settings
- Updated all tests and documentation

All tests passing: ✅ 129/129

## Update: Behavior Settings Group

After initial implementation, the `auto_copy_on_update` setting was moved from the `audio` group to a new `behavior` group, as it's more related to application behavior than audio functionality. This improves the logical organization of settings.
