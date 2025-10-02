# Settings Dialog Tab Order Change

## Overview

Changed the order of tabs in the Settings dialog to place "TOTP Defaults" as the last tab.

## Rationale

The "TOTP Defaults" tab contains advanced settings that users typically configure less frequently. Placing it last provides a better user experience by prioritizing more commonly used settings (Behavior, Audio) first.

## Changes Made

### 1. Settings Dialog (`simple_otp/ui/settings_dialog.py`)

**Updated tab order in `_create_ui()` method:**

```python
# Before
self._create_totp_page()
self._create_behavior_page()
self._create_audio_page()

# After
self._create_behavior_page()
self._create_audio_page()
self._create_totp_page()
```

**New tab order:**
1. Behavior
2. Audio
3. TOTP Defaults

### 2. Tests (`tests/test_settings_dialog.py`)

**Updated test expectations:**
```python
# Check page titles
assert dialog.notebook.GetPageText(0) == "Behavior"
assert dialog.notebook.GetPageText(1) == "Audio"
assert dialog.notebook.GetPageText(2) == "TOTP Defaults"
```

### 3. Documentation

**Updated:**
- `docs/SETTINGS.md` - Updated tab order description
- `docs/BEHAVIOR_SETTINGS_GROUP.md` - Updated page order description

## Benefits

1. **Better UX**: Frequently used settings (Behavior, Audio) appear first
2. **Logical Flow**: Basic settings before advanced TOTP configuration
3. **Consistency**: Maintains user expectations for settings organization

## Test Results

✅ All 14 settings dialog tests pass
✅ No compilation errors
✅ All functionality preserved