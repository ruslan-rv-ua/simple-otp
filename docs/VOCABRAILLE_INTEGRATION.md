# VocaBraille Integration - Screen Reader Support

**Date:** October 3, 2025  
**Feature:** Screen reader support for OTP code pronunciation using VocaBraille library

## Overview

The TOTP dialog now includes integrated screen reader support via the [VocaBraille](https://github.com/ruslan-rv-ua/VocaBraille) library. This allows users to have OTP codes spoken aloud using their default screen reader (NVDA, JAWS, Narrator, etc.).

## Features

### 1. Manual OTP Pronunciation

Users can pronounce OTP codes on demand using keyboard shortcuts:

- **J** or **Enter** - Pronounce current OTP
- **F** or **Shift+Enter** - Pronounce next OTP

The codes are spoken digit by digit with spaces between them (e.g., "1 2 3 4 5 6") for better clarity.

### 2. Automatic OTP Pronunciation

A new setting allows automatic pronunciation of OTP codes when they update:

- **Setting:** `behavior.auto_speak_password`
- **Default:** `False` (disabled)
- **Location:** Settings → Behavior tab → "Automatically speak password when it updates"

When enabled, the TOTP dialog will automatically speak the new OTP code each time it refreshes (typically every 30 seconds).

## Implementation Details

### VocaBraille Configuration

- **Error Mode:** `ErrorsMode.IGNORE` - Speech errors are silently ignored to avoid disrupting the UI
- **Interrupt Mode:** `interrupt=True` - Speech always interrupts any ongoing speech for immediate feedback
- **Engine Selection:** Uses default screen reader (no manual engine configuration)
- **No Custom Parameters:** All screen reader settings (rate, volume, pitch) use defaults

### Integration Points

#### TOTPDialog (`simple_otp/ui/totp_dialog.py`)

1. **Initialization:**
   ```python
   self.vocabraille = VocaBraille(errors=ErrorsMode.IGNORE)
   ```
   - Gracefully handles initialization failures by setting `vocabraille` to `None`

2. **Speech Method:**
   ```python
   def _speak_otp(self, otp_code: str) -> None:
       """Speak OTP code using VocaBraille."""
       if self.vocabraille:
           formatted_code = format_otp(otp_code)
           self.vocabraille.say(formatted_code, interrupt=True)
   ```
   - Formats OTP as displayed in UI (e.g., "123456" → "12 34 56")
   - Always interrupts ongoing speech
   - Silently ignores errors

3. **Keyboard Shortcuts:**
   - `_on_pronounce_current()` - Gets current OTP and speaks it
   - `_on_pronounce_next()` - Calculates next OTP and speaks it

4. **Auto-Speak Integration:**
   - In `_update_codes_and_progress()`, checks `behavior.auto_speak_password` setting
   - Speaks new OTP code when it changes
   - Works correctly alongside auto-copy feature (both can be enabled simultaneously)
   - Tracks last spoken OTP to avoid duplicate announcements

### Settings Manager

**New Setting:**
```python
"behavior": {
    "auto_speak_password": False,  # Default disabled
}
```

### Settings Dialog

**New Checkbox:**
- **Label:** "Automatically speak password when it updates"
- **Help Text:** "When enabled, the new TOTP code will be automatically spoken using your default screen reader each time it refreshes."
- **Location:** Behavior tab, after "Hide passwords" option

## User Experience

### For Screen Reader Users

1. **Discovery:**
   - Screen reader users will find the auto-speak option in Settings
   - Keyboard shortcuts (J, F, Enter, Shift+Enter) are discoverable via accelerator table

2. **Workflow Options:**
   - **Manual Mode (default):** Press J or Enter to hear current OTP when needed
   - **Automatic Mode:** Enable auto-speak setting for hands-free updates

3. **Integration with Existing Features:**
   - Works alongside auto-copy feature (can enable both)
   - Works with hidden password mode (codes are spoken even when hidden)
   - Works with audio alerts (warning sounds and copy sounds)

### Speech Behavior

- **Interrupt-based:** New speech always interrupts old speech
- **Clear pronunciation:** Digits spoken in pairs (e.g., "12 34 56") matching visual display
- **No configuration needed:** Uses system's default screen reader settings
- **Fail-safe:** If VocaBraille fails, feature is silently disabled (no errors shown)
- **Works with auto-copy:** Both auto-copy and auto-speak can be enabled together

## Translations

### English (en-US)
```json
"settings.behavior.auto_speak_password": "Automatically speak password when it updates"
"settings.behavior.auto_speak_password_help": "When enabled, the new TOTP code will be automatically\nspoken using your default screen reader each time it refreshes."
```

### Ukrainian (uk-UA)
```json
"settings.behavior.auto_speak_password": "Автоматично промовляти пароль при оновленні"
"settings.behavior.auto_speak_password_help": "Коли увімкнено, новий код TOTP буде автоматично\nпромовлятися за допомогою вашого типового читача екрана при кожному оновленні."
```

## Testing

### Test Coverage

1. **VocaBraille Initialization:**
   - Tests that VocaBraille is initialized (or None if it fails)

2. **Speech Method:**
   - Verifies `_speak_otp()` formats OTP correctly (grouped by 2 digits, matching display)
   - Verifies `interrupt=True` is always used

3. **Keyboard Shortcuts:**
   - Tests `_on_pronounce_current()` speaks current OTP
   - Tests `_on_pronounce_next()` speaks next OTP

4. **Auto-Speak:**
   - Verifies default setting is `False`
   - Tests auto-speak triggers on password update
   - Verifies no duplicate announcements

5. **Settings Dialog:**
   - Tests checkbox loads/saves setting correctly
   - Verifies default value is `False`

6. **Integration:**
   - Tests that auto-copy and auto-speak work together when both enabled

### Running Tests

```cmd
REM Run TOTP dialog tests
uv run pytest tests/test_totp_dialog.py -v

REM Run settings dialog tests
uv run pytest tests/test_settings_dialog.py -v

REM Run all tests
uv run pytest
```

## Dependencies

- **VocaBraille:** `>=0.1.0` (already in `pyproject.toml`)
- Automatically uses Windows speech APIs via UniversalSpeech library
- No additional installation required beyond `uv sync`

## Future Enhancements

Possible future improvements (not currently implemented):

1. **Configurable Speech Rate:** Allow users to adjust speech speed
2. **Voice Selection:** Allow users to choose specific TTS voice
3. **Phonetic Alphabet Mode:** Option to speak using NATO phonetic alphabet
4. **Braille Display Support:** Use VocaBraille's braille output feature
5. **Custom Pronunciation:** Allow users to customize how digits are spoken

## Accessibility Notes

This feature significantly improves accessibility for:
- Blind users relying on screen readers
- Users with low vision who benefit from audio confirmation
- Users with dyslexia who may find audio easier than visual reading
- Users in situations where hands-free operation is beneficial

The implementation follows accessibility best practices:
- Always interrupts for immediate feedback
- Works with hidden password mode
- No configuration required (respects system defaults)
- Graceful degradation if speech fails
- Clear, digit-by-digit pronunciation

## Related Files

- `simple_otp/ui/totp_dialog.py` - Main implementation
- `simple_otp/core/settings_manager.py` - Settings default
- `simple_otp/ui/settings_dialog.py` - Settings UI
- `simple_otp/locales/en-US.json` - English translations
- `simple_otp/locales/uk-UA.json` - Ukrainian translations
- `tests/test_totp_dialog.py` - TOTP dialog tests
- `tests/test_settings_dialog.py` - Settings dialog tests
- `pyproject.toml` - VocaBraille dependency

## References

- [VocaBraille GitHub Repository](https://github.com/ruslan-rv-ua/VocaBraille)
- [VocaBraille API Documentation](https://github.com/ruslan-rv-ua/VocaBraille#api-reference)
- [UniversalSpeech Library](https://github.com/qtnc/UniversalSpeech)
