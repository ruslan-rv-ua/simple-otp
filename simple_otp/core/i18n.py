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
    i18n.unload_everything()  # TODO: use reload_everything if available
    i18n.load_everything(locale=locale, lock=True)
    i18n.set("locale", locale)


def init_i18n() -> None:
    """Initialize i18n configuration for the application."""
    # Configure paths and defaults used by i18n
    i18n.load_path.append(str(locales_dir))
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("skip_locale_root_data", True)
    i18n.set("fallback", "en")


# Expose translation function as `_` for convenience
_ = i18n.t
