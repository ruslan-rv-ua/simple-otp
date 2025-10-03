# Hide Passwords Feature

## Overview
Added a new "Hide Passwords" feature to the application settings that allows users to hide OTP codes in the TOTP dialog for enhanced privacy.

## Implementation Details

### 1. Settings Manager (`simple_otp/core/settings_manager.py`)
- Added `"hide_passwords": True` to the `behavior` section of `DEFAULT_SETTINGS`
- Default value is `True` (passwords are hidden by default)

### 2. Settings Dialog (`simple_otp/ui/settings_dialog.py`)
- Added checkbox control `hide_passwords_check` in the behavior settings page
- Positioned between auto-copy and open-last-file settings
- Includes help text explaining the feature
- Implemented load/save logic in `_load_settings()` and `_save_settings()`

### 3. Localization (`simple_otp/locales/`)
Added translations in both `en-US.json` and `uk-UA.json`:
- **English:**
  - `settings.behavior.hide_passwords`: "Hide passwords in TOTP dialog"
  - `settings.behavior.hide_passwords_help`: "When enabled, OTP codes are displayed as '******' and cannot be focused with keyboard navigation."

- **Ukrainian:**
  - `settings.behavior.hide_passwords`: "Приховувати паролі в діалозі TOTP"
  - `settings.behavior.hide_passwords_help`: "Коли увімкнено, коди OTP відображаються як '******' і не можуть бути сфокусовані за допомогою клавіатури."

### 4. TOTP Dialog (`simple_otp/ui/totp_dialog.py`)
- Added `self.hide_passwords` attribute that reads from settings during initialization
- Modified text control creation:
  - `AcceptsFocusFromKeyboard = lambda: True` is only applied when `hide_passwords` is `False`
  - When `True`, text controls cannot receive keyboard focus
- Updated `_update_codes_and_progress()` method:
  - Displays `"******"` instead of formatted OTP codes when `hide_passwords` is `True`
  - Still calculates actual OTP codes for copying purposes
- Updated copy methods:
  - `_on_copy_current()` now gets OTP directly from `self.totp.now()` instead of reading from text control
  - `_on_copy_next()` calculates and gets next OTP directly from `self.totp.at(next_time)`
  - This ensures copying works correctly even when OTP codes are hidden

## Behavior

### When `hide_passwords = True` (default):
1. OTP text fields display static text: `"******"`
2. Text fields cannot be focused using Tab or keyboard navigation
3. Copy buttons still work - they copy the actual OTP code to clipboard
4. Auto-copy functionality (if enabled) still works correctly
5. Progress bar and countdown continue to function normally

### When `hide_passwords = False`:
1. OTP text fields display actual formatted codes (e.g., "12 34 56")
2. Text fields can be focused using Tab or keyboard navigation
3. All other functionality remains unchanged

## User Experience
- Users can toggle this setting at any time in Settings > Behavior
- Changes take effect the next time the TOTP dialog is opened
- The setting persists across application restarts
- Enhanced privacy when displaying OTP codes on shared screens or during screen recordings
