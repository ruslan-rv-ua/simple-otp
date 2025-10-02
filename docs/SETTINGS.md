# Settings System Documentation

## Overview

The settings system provides a flexible mechanism for managing application configuration with JSON-based persistence. Settings are stored in a `settings.json` file located next to `__main__.py` in the application directory.

## Architecture

### SettingsManager

The `SettingsManager` class (`simple_otp/core/settings_manager.py`) handles all settings operations:

- **Loading**: Reads settings from JSON file, merging with defaults
- **Saving**: Writes current settings to JSON file
- **Access**: Provides get/set methods with dot-notation for nested settings
- **Reset**: Allows resetting to default values

### SettingsDialog

The `SettingsDialog` class (`simple_otp/ui/settings_dialog.py`) provides a user interface for viewing and modifying settings:

- **Tabbed Interface**: Settings organized into categories (Behavior, Audio, TOTP Defaults)
- **Validation**: Ensures valid values before saving
- **Reset Functionality**: Allows restoring defaults with confirmation

## Default Settings Structure

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

## Settings Categories

### TOTP Default Settings

Default values used when adding new TOTP accounts:

- **default_digits**: Default number of digits for new accounts (6, 7, or 8)
- **default_interval**: Default time interval in seconds (15-120)
- **default_digest**: Default hash algorithm (SHA1, SHA256, SHA512)

These settings are automatically applied when opening the Add Account dialog, providing convenient defaults while still allowing users to customize each account individually.

### Behavior Settings

Controls application behavior:

- **auto_copy_on_update**: Automatically copy new password to clipboard when it updates

### Audio Settings

Controls sound effects:

- **play_password_copied_sound**: Play sound when password is copied to clipboard
- **play_warning_sound**: Play warning sound before password expires
- **warning_sound_seconds**: Seconds before expiration to play warning (1-15)

## Usage

### Accessing Settings in Code

```python
from simple_otp.core.settings_manager import SettingsManager

# Create settings manager (uses default location)
settings = SettingsManager()

# Get a setting value (dot notation for nested settings)
digits = settings.get("totp.default_digits")
play_sound = settings.get("audio.play_password_copied_sound")

# Get with default value if not found
custom_setting = settings.get("custom.key", "default_value")

# Set a setting value
settings.set("totp.default_digits", 8)
settings.set("audio.warning_sound_seconds", 10)

# Save changes to file
settings.save()

# Reset to defaults
settings.reset_to_defaults()
settings.save()

# Get all settings as dictionary
all_settings = settings.get_all()
```

### Opening Settings Dialog

From the main window:

1. **Menu**: Tools → Settings (or press `Ctrl+,`)
2. **Modify settings** in the tabbed interface
3. **Click OK** to save or **Cancel** to discard changes
4. **Reset to Defaults** button restores all defaults (with confirmation)

## File Location

The settings file is automatically created at:

```
simple_otp/settings.json
```

This is in the same directory as `__main__.py`, making it part of the application package.

## Persistence Behavior

- **First Run**: Settings file is created with default values
- **Corrupted File**: Falls back to defaults and attempts to overwrite
- **Missing Keys**: Missing settings are merged with defaults on load
- **Concurrent Access**: Multiple `SettingsManager` instances can work with the same file (last save wins)

## Error Handling

The `SettingsManager` handles several error cases gracefully:

1. **Missing File**: Creates new file with defaults
2. **Invalid JSON**: Uses defaults and overwrites file on save
3. **I/O Errors**: Silently fails during load (uses defaults), propagates during explicit save
4. **Missing Keys**: Merges loaded settings with defaults to fill gaps

## Adding New Settings

To add a new setting:

1. **Update `DEFAULT_SETTINGS`** in `SettingsManager`:
   ```python
   DEFAULT_SETTINGS = {
       # ... existing settings ...
       "new_category": {
           "new_setting": default_value
       }
   }
   ```

2. **Add UI controls** in `SettingsDialog`:
   - Create new page or add to existing page
   - Add controls in `_create_*_page()` method
   - Load values in `_load_settings()`
   - Save values in `_save_settings()`

3. **Write tests** for the new setting:
   - Test in `test_settings_manager.py` (get/set/persistence)
   - Test in `test_settings_dialog.py` (UI integration)

4. **Update documentation** with setting description and usage

## Testing

Run tests for the settings system:

```cmd
REM Run all settings tests
uv run pytest tests/test_settings_manager.py tests/test_settings_dialog.py -v

REM Run only settings manager tests
uv run pytest tests/test_settings_manager.py -v

REM Run only settings dialog tests
uv run pytest tests/test_settings_dialog.py -v
```

## Current Implementation Status

### Fully Implemented ✅

- Settings persistence (JSON file storage)
- Settings manager with get/set/reset functionality
- Settings dialog with tabbed interface
- Integration with main window (Tools menu)
- Default settings structure
- Unit tests for manager and dialog
- **TOTP Defaults** - Applied when adding new accounts
- **Audio Settings** - Controls sound effects and auto-copy behavior

### Key Features

#### TOTP Defaults
When opening the "Add Account" dialog, the default values for digits, interval, and digest algorithm are automatically loaded from settings. This provides a convenient starting point while still allowing per-account customization.

#### Behavior Settings
- **Auto-Copy on Update**: Automatically copy new TOTP code to clipboard when it refreshes

#### Audio Settings
- **Sound Effects**: Enable/disable sounds for password copy and expiration warning
- **Warning Timing**: Configure how many seconds before expiration to play the warning sound

## Future Enhancements

Potential additions to the settings system:

1. **Settings validation** with custom validators
2. **Settings migration** for version upgrades
3. **Import/export** settings functionality
4. **Per-user settings** vs system-wide settings
5. **Settings search** for large settings dialogs
6. **Settings backup** and restore
7. **Settings profiles** for different use cases
