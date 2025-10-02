"""Entry point for simple-otp application."""

from pathlib import Path

import wx

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.core.i18n import _, set_locale
from simple_otp.ui.main_window import MainWindow
from simple_otp.ui.password_dialog import PasswordDialog

# Set locale at module load
set_locale("uk-UA")  # TODO: make dynamic based on user settings


def authenticate(file_path: Path) -> str | None:
    """
    Perform authentication for a specific accounts file.

    Args:
        file_path: Path to the accounts file to authenticate against

    Returns:
        The validated password if successful, None if user cancelled
        or failed authentication
    """
    # Create accounts manager for the specific file
    accounts_manager = AccountsManager(storage_path=file_path, auto_create=False)

    # Ask for password to verify
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        remaining = max_attempts - attempt + 1

        if attempt == 1:
            message = _("authentication.enter_password").format(filename=file_path.name)
        else:
            message = _("authentication.incorrect_password").format(
                remaining=remaining, filename=file_path.name
            )

        dialog = PasswordDialog(
            None,
            title=_("authentication.title"),
            message=message,
            require_confirmation=False,
        )

        if dialog.ShowModal() != wx.ID_OK:
            dialog.Destroy()
            return None

        password = dialog.GetPassword()
        dialog.Destroy()

        # Verify password by trying to decrypt accounts
        if accounts_manager.verify_password(password):
            return password

        # If this was the last attempt, show error
        if attempt == max_attempts:
            wx.MessageBox(
                _("authentication.max_attempts_exceeded"),
                _("authentication.failed"),
                wx.OK | wx.ICON_ERROR,
            )

    return None


def main():
    """Launch the Simple OTP application."""
    from simple_otp.core.settings_manager import SettingsManager

    app = wx.App()

    # Load settings to determine which file to open
    settings_manager = SettingsManager()
    accounts_file = None
    password = None

    # Check if we should try to open the last file
    if settings_manager.get("files.open_last_file_on_startup", True):
        recent_files = settings_manager.get("files.recent_files", [])
        if recent_files:
            last_file_path = Path(recent_files[0])

            # Check if the file exists
            if last_file_path.exists():
                # Authenticate against this specific file
                password = authenticate(last_file_path)
                if password:
                    accounts_file = last_file_path
                else:
                    # User cancelled authentication - exit
                    return

    # If no file selected yet, user will need to create/open one from UI
    # Create and show main window (possibly with no file)
    frame = MainWindow(None, password, accounts_file)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
