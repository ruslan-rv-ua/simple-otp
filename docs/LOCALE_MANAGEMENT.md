# Locale Management Feature

## Overview

The Simple OTP application now supports multiple languages with automatic locale detection and manual language selection through the user interface.

## Features

### 1. Automatic Locale Detection

When the application starts for the first time (when no locale is stored in settings):
- The system automatically detects the Windows user locale
- The detected locale is saved to the application settings
- If detection fails or the system is not Windows, defaults to `en-US`

### 2. Manual Language Selection

Users can manually change the application language through the menu:
- **English**: `Options > Language > English`
- **Ukrainian**: `Опції > Мова > Українська`

Language names are displayed in their native language for better user experience.

### 3. Settings Persistence

The selected locale is stored in `settings.json`:
```json
{
  "locale": "uk-UA",
  ...
}
```

When `locale` is `null`, the system will auto-detect on the next startup.

## Supported Locales

Currently supported locales:
- `en-US` - English (United States)
- `uk-UA` - Ukrainian (Ukraine)

To add more locales, create a new JSON file in `simple_otp/locales/` with the locale code as the filename (e.g., `de-DE.json`).

## Implementation Details

### Architecture

1. **Settings Storage**: Locale preference is stored in `SettingsManager` under the key `"locale"`
2. **Auto-Detection**: `get_windows_locale()` uses Windows API to retrieve user locale on Windows systems
3. **Initialization**: `init_i18n()` configures the i18n library and loads translations
4. **Dynamic Switching**: `set_locale()` allows runtime locale changes

### Key Files

- `simple_otp/core/i18n.py` - i18n utilities and initialization
- `simple_otp/core/settings_manager.py` - Settings storage including locale
- `simple_otp/__main__.py` - Application entry point with locale initialization
- `simple_otp/ui/main_window.py` - Language selection menu UI
- `simple_otp/locales/*.json` - Translation files for each locale

### Menu Structure Change

The "Tools" menu has been renamed to "Options" in all locales:
- **English**: `&Tools` → `&Options`
- **Ukrainian**: `&Інструменти` → `&Опції`

The new Options menu structure:
```
Options
├── Language
│   ├── English
│   └── Українська
├── ──────────────
└── Settings...
```

## User Experience

### First Run

1. Application detects Windows locale (e.g., `uk-UA`)
2. Saves detected locale to settings
3. Loads Ukrainian translations
4. UI displays in Ukrainian

### Changing Language

1. User opens `Options > Language` menu
2. Selects desired language (e.g., `English`)
3. Application saves selection to settings
4. Locale is applied immediately
5. User sees notification: "The application needs to restart for the language change to take full effect."
6. On next restart, full UI is in selected language

## API Reference

### `get_windows_locale() -> str | None`

Returns the current Windows user locale or `None` on non-Windows systems.

**Example:**
```python
from simple_otp.core.i18n import get_windows_locale

locale = get_windows_locale()  # e.g., "uk-UA" or "en-US"
```

### `get_available_locales() -> list[str]`

Returns a sorted list of available locales based on JSON files in the locales directory.

**Example:**
```python
from simple_otp.core.i18n import get_available_locales

locales = get_available_locales()  # ["en-US", "uk-UA"]
```

### `set_locale(locale: str) -> None`

Sets the current locale for translations.

**Example:**
```python
from simple_otp.core.i18n import set_locale

set_locale("uk-UA")
```

### `init_i18n(locale: str | None = None, auto_detect: bool = True) -> None`

Initializes the i18n configuration.

**Parameters:**
- `locale`: Optional locale to use. If `None` and `auto_detect` is `True`, attempts to detect Windows locale.
- `auto_detect`: If `True` and locale is `None`, auto-detect Windows locale. If `False` and locale is `None`, use `"en-US"`.

**Example:**
```python
from simple_otp.core.i18n import init_i18n

# Auto-detect locale
init_i18n()

# Use specific locale
init_i18n(locale="uk-UA", auto_detect=False)

# Use default without detection
init_i18n(locale=None, auto_detect=False)
```

## Testing

Tests have been added to verify locale functionality:

### Settings Manager Tests (`test_settings_manager.py`)
- `test_locale_default_is_none` - Verifies locale defaults to `None`
- `test_set_locale` - Tests setting and getting locale values
- `test_locale_persistence` - Ensures locale persists across save/load

### i18n Module Tests (`test_i18n.py`)
- `test_get_available_locales_returns_list` - Verifies locale list retrieval
- `test_get_windows_locale_returns_string_or_none` - Tests Windows locale detection
- `test_set_locale_en_us` - Tests English locale
- `test_set_locale_uk_ua` - Tests Ukrainian locale
- `test_init_i18n_with_explicit_locale` - Tests explicit initialization
- `test_init_i18n_no_auto_detect` - Tests initialization without detection
- `test_locale_switch_changes_translations` - Verifies locale switching

Run tests with:
```cmd
uv run pytest tests/test_settings_manager.py tests/test_i18n.py
```

## Future Enhancements

Potential improvements for locale management:

1. **Instant UI Update**: Implement full UI refresh on locale change without requiring restart
2. **More Languages**: Add support for more locales (Spanish, German, French, etc.)
3. **Date/Time Formatting**: Locale-aware date and time display
4. **Number Formatting**: Locale-specific number formatting
5. **Keyboard Shortcuts**: Locale-aware keyboard shortcut display
6. **Language Detection Priority**: Detect language from environment variables on non-Windows systems

## Migration Notes

For users upgrading from previous versions:

1. **No Breaking Changes**: Existing settings files will work without modification
2. **Auto-Detection**: On first run after upgrade, the system will detect and save the current Windows locale
3. **Menu Structure**: Users will see "Options" instead of "Tools" in the menu bar
4. **New Menu Item**: The "Language" submenu will appear at the top of the Options menu

## Troubleshooting

### Language Not Changing

If the language doesn't change after selection:
1. Ensure you restart the application after changing language
2. Check that the locale file exists in `simple_otp/locales/`
3. Verify settings.json contains the correct locale value

### Wrong Language on Startup

If the wrong language appears on startup:
1. Open `simple_otp/settings.json`
2. Check the `"locale"` value
3. Set to desired locale (e.g., `"en-US"` or `"uk-UA"`)
4. Restart application

### Locale Detection Not Working

If Windows locale detection fails:
1. The application will default to `en-US`
2. Manually select language from `Options > Language` menu
3. The selected language will be used on future startups
