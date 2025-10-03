# Test Updates for Hide Passwords Feature

## Overview
Updated existing tests and added new test cases to cover the "hide passwords" functionality.

## Test Files Updated

### 1. `tests/test_settings_manager.py`

#### Updated Tests:
- **`test_behavior_settings_defaults`**: Added assertion to verify `behavior.hide_passwords` defaults to `True`
- **`test_modify_behavior_settings`**: Added test case for setting and getting `behavior.hide_passwords`

#### Test Coverage:
- ✅ Default value is `True`
- ✅ Can be set to `False`
- ✅ Persists across save/load cycles

---

### 2. `tests/test_settings_dialog.py`

#### Updated Tests:
- **`test_default_values_in_ui`**: Added assertion to verify `hide_passwords_check` checkbox defaults to `True`

#### New Tests:
- **`test_hide_passwords_checkbox`**: Comprehensive test for the hide passwords checkbox
  - Tests loading `True` from settings
  - Tests loading `False` from settings
  - Tests saving `True` to settings
  - Tests saving `False` to settings

#### Test Coverage:
- ✅ Checkbox exists and is accessible
- ✅ Default value is `True` in UI
- ✅ Loads correctly from settings manager
- ✅ Saves correctly to settings manager
- ✅ Bidirectional binding works properly

---

### 3. `tests/test_totp_dialog.py`

#### Fixed Tests (Critical):
- **`test_copy_current_button`**: Changed to verify actual OTP is copied, not text control value
  - Previously: Compared copied text with `dialog.current_text.GetValue().replace(" ", "")`
  - Now: Verifies copied text is a valid 6-8 digit number
  - **Why**: With `hide_passwords=True`, text control shows "******" but clipboard gets real OTP

- **`test_copy_next_button`**: Same fix as above for next OTP button

- **`test_update_codes_and_progress`**: Added conditional check for hidden vs visible passwords
  - When `hide_passwords=True`: Expects "******" in text controls
  - When `hide_passwords=False`: Expects formatted codes with spaces

#### New Tests:
1. **`test_hide_passwords_enabled_by_default`**
   - Verifies `hide_passwords` setting defaults to `True`
   - Verifies dialog instance reads the setting correctly

2. **`test_passwords_hidden_when_enabled`**
   - Sets `hide_passwords=True` in settings
   - Creates dialog and updates codes
   - Verifies text controls display "******"

3. **`test_passwords_visible_when_disabled`**
   - Sets `hide_passwords=False` in settings
   - Creates dialog and updates codes
   - Verifies text controls display formatted OTP codes (e.g., "12 34 56")
   - Verifies codes contain spaces (formatting)

4. **`test_keyboard_focus_disabled_when_passwords_hidden`**
   - Sets `hide_passwords=True`
   - Verifies `AcceptsFocusFromKeyboard` is NOT overridden
   - Text controls should use default read-only behavior (no keyboard focus)

5. **`test_keyboard_focus_enabled_when_passwords_visible`**
   - Sets `hide_passwords=False`
   - Verifies `AcceptsFocusFromKeyboard()` returns `True` for both text controls
   - Text controls can receive keyboard focus for accessibility

6. **`test_copy_works_with_hidden_passwords`**
   - Sets `hide_passwords=True`
   - Verifies text control shows "******"
   - Simulates copy button click
   - Verifies actual OTP code is copied (not "******")
   - Verifies copied code is 6 digits and all numeric

#### Test Coverage:
- ✅ Default behavior with `hide_passwords=True`
- ✅ Display shows "******" when hidden
- ✅ Display shows formatted codes when visible
- ✅ Keyboard focus disabled when hidden
- ✅ Keyboard focus enabled when visible
- ✅ Copy functionality works correctly with hidden passwords
- ✅ Copy functionality works correctly with visible passwords
- ✅ Copied text is always the real OTP code

---

## Test Results

All tests pass successfully:

```
tests/test_settings_manager.py:  23 passed
tests/test_settings_dialog.py:   15 passed
tests/test_totp_dialog.py:       14 passed
```

**Total: 52 tests passed, 0 failed**

---

## Key Testing Insights

### Critical Issue Fixed
The original `test_copy_current_button` and `test_copy_next_button` tests would have **failed** with the new feature because they verified the copied text by reading from `dialog.current_text.GetValue()`. With `hide_passwords=True` (the default), this would return "******", not the actual OTP code.

**Solution**: Changed verification to check that:
1. A value was copied
2. The value is numeric (digits only)
3. The value has the correct length (6-8 digits)

This approach works correctly regardless of the `hide_passwords` setting.

### Test Design Principles Applied
1. **Test behavior, not implementation**: Verify outcomes (clipboard content, display text) rather than internal state
2. **Test both paths**: Both `hide_passwords=True` and `hide_passwords=False` scenarios
3. **Test integration**: Verify that copy buttons work correctly even when passwords are hidden
4. **Test defaults**: Ensure default behavior is secure (passwords hidden by default)

---

## Regression Prevention
These tests ensure that:
- Future changes won't accidentally break password hiding
- Copy functionality always works regardless of display setting
- Settings are properly persisted and loaded
- UI controls reflect the current settings state
- Default behavior prioritizes privacy (passwords hidden)
