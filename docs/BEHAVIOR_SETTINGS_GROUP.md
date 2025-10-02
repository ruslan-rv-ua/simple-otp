# Behavior Settings Group - Change Summary

## Overview

Moved the `auto_copy_on_update` setting from the `audio` group to a new `behavior` group for better logical organization.

## Rationale

The "Automatically copy password to clipboard when it updates" setting is not related to audio functionality. It's an application behavior setting that controls clipboard operations, not sound effects.

## Changes Made

### 1. Settings Structure

**Before:**
```json
{
  "audio": {
    "play_password_copied_sound": true,
    "play_warning_sound": true,
    "warning_sound_seconds": 5,
    "auto_copy_on_update": false
  }
}
```

**After:**
```json
{
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

### 2. Settings Dialog

**Created new "Behavior" page:**
- Moved auto-copy checkbox from Audio page to new Behavior page
- Added helpful description text
- Dialog now has 3 pages: Behavior, Audio, TOTP Defaults

### 3. Code Updates

**Updated references:**
- `simple_otp/core/settings_manager.py` - Added `behavior` group to defaults
- `simple_otp/ui/settings_dialog.py` - Created `_create_behavior_page()` method
- `simple_otp/ui/totp_dialog.py` - Updated to use `behavior.auto_copy_on_update`
- `simple_otp/settings.json` - Updated structure

### 4. Tests

**Updated all affected tests:**
- Split audio settings tests into separate audio and behavior tests
- Updated test for settings dialog page count (now 3 pages)
- All 129 tests pass ✅

### 5. Documentation

**Updated:**
- `docs/SETTINGS.md` - Added Behavior Settings section
- `docs/TOTP_DEFAULTS_UPDATE.md` - Added update note

## Benefits

1. **Better Organization**: Settings are grouped by their actual purpose
2. **Scalability**: Behavior group can accommodate future non-audio behavior settings
3. **User Experience**: More intuitive settings dialog structure
4. **Code Clarity**: Clear separation of concerns

## Migration

Existing `settings.json` files will automatically migrate:
- Settings manager merges loaded settings with new defaults
- Old `audio.auto_copy_on_update` values will be ignored
- New `behavior.auto_copy_on_update` will use default value (false)
- No user action required

## Future Enhancements

The new `behavior` group can accommodate additional settings such as:
- Auto-lock timeout
- Confirmation dialogs preferences
- Default window size/position
- Application startup behavior
