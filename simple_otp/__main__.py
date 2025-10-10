"""Entry point for simple-otp application."""

import wx

from simple_otp.core.i18n import get_windows_locale, init_i18n
from simple_otp.core.settings_manager import SettingsManager
from simple_otp.ui.main_window import MainWindow


def main():
    """Launch the Simple OTP application."""
    app = wx.App()

    # Load settings to determine locale
    settings_manager = SettingsManager()

    # Initialize locale from settings
    saved_locale = settings_manager.get("locale")
    if saved_locale is None:
        # Auto-detect Windows locale and save it
        detected_locale = get_windows_locale() or "en-US"
        settings_manager.set("locale", detected_locale)
        settings_manager.save()
        init_i18n(locale=detected_locale, auto_detect=False)
    else:
        # Use saved locale
        init_i18n(locale=saved_locale, auto_detect=False)

    # Create and show main window
    # MainWindow will handle opening last file if configured
    frame = MainWindow(None)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
