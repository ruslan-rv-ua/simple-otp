"""Unit tests for i18n module."""

from simple_otp.core.i18n import (
    get_available_locales,
    get_locale_native_name,
    get_windows_locale,
    init_i18n,
    set_locale,
)


class TestI18n:
    """Test cases for the i18n module."""

    def test_get_available_locales_returns_list(self):
        """Test that get_available_locales returns a list of locale codes."""
        locales = get_available_locales()

        assert isinstance(locales, list)
        assert len(locales) > 0
        # Should have at least en-US and uk-UA
        assert "en-US" in locales
        assert "uk-UA" in locales

    def test_get_available_locales_sorted(self):
        """Test that available locales are returned sorted."""
        locales = get_available_locales()

        # Check that list is sorted
        assert locales == sorted(locales)

    def test_get_windows_locale_returns_string_or_none(self):
        """Test that get_windows_locale returns string or None."""
        locale = get_windows_locale()

        # Should be either None (on non-Windows) or a string
        assert locale is None or isinstance(locale, str)

        # If a string, should have format like "en-US", "uk-UA"
        if locale:
            assert "-" in locale or "_" in locale

    def test_set_locale_en_us(self):
        """Test setting locale to English."""
        set_locale("en-US")

        # Import translation function after setting locale
        from simple_otp.core.i18n import _

        # Test a simple translation
        title = _("main.title")
        assert title == "Simple OTP"

    def test_set_locale_uk_ua(self):
        """Test setting locale to Ukrainian."""
        set_locale("uk-UA")

        # Import translation function after setting locale
        from simple_otp.core.i18n import _

        # Test a simple translation
        title = _("main.title")
        assert title == "Simple OTP"

        # Test a Ukrainian-specific translation
        search = _("main.search")
        assert search == "Швидкий пошук:"

    def test_init_i18n_with_explicit_locale(self):
        """Test initializing i18n with explicit locale."""
        init_i18n(locale="en-US", auto_detect=False)

        from simple_otp.core.i18n import _

        title = _("main.title")
        assert title == "Simple OTP"

    def test_init_i18n_no_auto_detect(self):
        """Test initializing i18n without auto-detection."""
        init_i18n(locale=None, auto_detect=False)

        from simple_otp.core.i18n import _

        # Should default to en-US
        search = _("main.search")
        assert search == "Fast Search:"

    def test_translation_key_format(self):
        """Test that translation keys work with dot notation."""
        set_locale("en-US")

        from simple_otp.core.i18n import _

        # Test nested keys
        assert _("main.title") == "Simple OTP"
        assert _("main.menu.file.file") == "&File"
        assert _("main.menu.options.options") == "&Options"

    def test_locale_switch_changes_translations(self):
        """Test that switching locales changes translations."""
        # Start with English
        set_locale("en-US")
        from simple_otp.core.i18n import _

        english_search = _("main.search")
        assert english_search == "Fast Search:"

        # Switch to Ukrainian
        set_locale("uk-UA")

        ukrainian_search = _("main.search")
        assert ukrainian_search == "Швидкий пошук:"

        # Verify they're different
        assert english_search != ukrainian_search

    def test_get_locale_native_name_en_us(self):
        """Test getting native name for English locale."""
        name = get_locale_native_name("en-US")
        assert name == "English"

    def test_get_locale_native_name_uk_ua(self):
        """Test getting native name for Ukrainian locale."""
        name = get_locale_native_name("uk-UA")
        assert name == "Українська"

    def test_get_locale_native_name_missing_locale(self):
        """Test that missing locale returns the code itself."""
        name = get_locale_native_name("xx-XX")
        assert name == "xx-XX"
