"""Entry point for simple-otp application."""

import wx

from simple_otp.core.i18n import get_windows_locale, init_i18n
from simple_otp.core.logger import configure_logging, logger
from simple_otp.core.settings_manager import SettingsManager
from simple_otp.ui.main_window import MainWindow


def main():
    """Launch the Simple OTP application."""
    # Initialize logging first to capture all application events
    configure_logging()
    logger.info("Starting Simple OTP application")

    app = wx.App()
    logger.debug("wxPython App instance created")

    try:
        # Load settings to determine locale
        logger.debug("Loading settings manager")
        settings_manager = SettingsManager()

        # Initialize locale from settings
        saved_locale = settings_manager.get("locale")
        if saved_locale is None:
            # Auto-detect Windows locale and save it
            logger.debug("No saved locale found, detecting system locale")
            detected_locale = get_windows_locale() or "en-US"
            logger.info(f"Detected system locale: {detected_locale}")
            settings_manager.set("locale", detected_locale)
            settings_manager.save()
            init_i18n(locale=detected_locale, auto_detect=False)
        else:
            # Use saved locale
            logger.info(f"Using saved locale: {saved_locale}")
            init_i18n(locale=saved_locale, auto_detect=False)

        # Create and show main window
        # MainWindow will handle opening last file if configured
        logger.debug("Creating main window")
        frame = MainWindow(None)
        frame.Show()
        logger.info("Main window displayed, entering main loop")
        app.MainLoop()
        logger.info("Application main loop ended")

    except Exception as e:
        logger.opt(exception=True).critical(f"Fatal error in main(): {e}")
        raise


if __name__ == "__main__":
    main()
