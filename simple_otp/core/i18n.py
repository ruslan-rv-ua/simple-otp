"""i18n helpers and initialization for simple-otp.

This module configures the `i18n` package for the application and
provides small helpers such as `get_windows_locale()` and `set_locale()`.

By default `init_i18n()` is called at import time to preserve the
previous behaviour. Tests or other entry points can call `init_i18n(auto=False)`
to avoid performing the initialization automatically.

Notes:
- `get_windows_locale()` is Windows-specific and returns None on other
  platforms.
"""

from __future__ import annotations

import ctypes
import sys
from pathlib import Path

import i18n

locales_dir = Path(__file__).parent.parent / "locales"

# Maximum locale name buffer length for Windows API (per Microsoft docs)
LOCALE_NAME_MAX_LENGTH = 85


def get_windows_locale() -> str | None:  # -> e.g. "uk-UA"
    """Return the current Windows user locale (e.g. "uk-UA") or None.

    This function is safe to call on non-Windows platforms — it will
    simply return None.
    """
    if not sys.platform.startswith("win"):
        return None

    try:
        windll = ctypes.windll.kernel32
        locale_name = ctypes.create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)
        windll.GetUserDefaultLocaleName(locale_name, LOCALE_NAME_MAX_LENGTH)
        return locale_name.value or None
    except Exception:  # narrow to Exception to avoid hiding system exits
        # Failure to detect Windows locale — return None
        return None


def set_locale(locale: str) -> None:
    """Set the current locale for translations.

    This unloads and reloads translation data and sets the active locale
    in the `i18n` package.
    """
    i18n.unload_everything()
    i18n.load_everything(locale=locale, lock=True)
    i18n.set("locale", locale)


def get_available_locales() -> list[str]:
    """Return list of available locales based on JSON files in locales directory.

    Returns:
        List of locale codes (e.g., ["en-US", "uk-UA"])
    """
    available = []
    if locales_dir.exists():
        for file in locales_dir.glob("*.json"):
            if file.stem not in ("", "."):
                available.append(file.stem)
    return sorted(available)


def get_locale_native_name(locale_code: str) -> str:
    """Get the native name of a locale from its locale file.

    Args:
        locale_code: Locale code (e.g., "en-US", "uk-UA")

    Returns:
        Native name of the locale (e.g., "English", "Українська"),
        or the locale code if the native name is not found.
    """
    import json

    locale_file = locales_dir / f"{locale_code}.json"
    if locale_file.exists():
        try:
            with locale_file.open(encoding="utf-8") as f:
                data = json.load(f)
                # Try to get native name from locale.native_name
                return data.get("locale", {}).get("native_name", locale_code)
        except (json.JSONDecodeError, OSError):
            pass
    return locale_code


def init_i18n(locale: str | None = None, auto_detect: bool = True) -> None:
    """Initialize i18n configuration for the application.

    Args:
        locale: Optional locale to use. If None and auto_detect is True,
                attempts to detect Windows locale or falls back to "en-US".
        auto_detect: If True and locale is None, auto-detect Windows locale.
                     If False and locale is None, use "en-US".
    """
    # Configure paths and defaults used by i18n
    i18n.load_path.append(str(locales_dir))
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("skip_locale_root_data", True)
    i18n.set("fallback", "en")

    # Determine which locale to load
    if locale is None:
        if auto_detect:
            locale = get_windows_locale() or "en-US"
        else:
            locale = "en-US"

    # Load translations for the selected locale
    set_locale(locale)


init_i18n()

# Expose translation function as `_` for convenience
_ = i18n.t
