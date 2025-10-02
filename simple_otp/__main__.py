"""Entry point for simple-otp application."""

import wx

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.ui.main_window import MainWindow
from simple_otp.ui.password_dialog import PasswordDialog


def authenticate() -> str | None:
    """
    Perform authentication flow.

    Returns:
        The validated password if successful, None if user cancelled
        or failed authentication
    """
    # Create accounts manager without auto-creating storage
    accounts_manager = AccountsManager(auto_create=False)

    # Check if accounts exist
    if not accounts_manager.storage_exists() or not accounts_manager.has_accounts():
        # First time setup - ask for password with confirmation
        dialog = PasswordDialog(
            None,
            title="Initial Setup",
            message=(
                "Welcome to Simple OTP!\n\n"
                "Please create a master password to encrypt your accounts:"
            ),
            require_confirmation=True,
        )

        if dialog.ShowModal() != wx.ID_OK:
            dialog.Destroy()
            return None

        password = dialog.GetPassword()
        dialog.Destroy()

        # Create initial account with the password
        try:
            accounts_manager.create_initial_account(password)
            wx.MessageBox(
                "Setup complete! A default example account has been created.\n\n"
                "You can delete it and add your own accounts later.",
                "Setup Complete",
                wx.OK | wx.ICON_INFORMATION,
            )
            return password
        except Exception as e:
            wx.MessageBox(
                f"Failed to create initial account: {str(e)}",
                "Setup Error",
                wx.OK | wx.ICON_ERROR,
            )
            return None
    else:
        # Existing accounts - ask for password to verify
        max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            remaining = max_attempts - attempt + 1

            if attempt == 1:
                message = "Enter your master password to unlock Simple OTP:"
            else:
                message = (
                    f"Incorrect password. {remaining} attempt(s) remaining.\n\n"
                    "Enter your master password:"
                )

            dialog = PasswordDialog(
                None,
                title="Authentication Required",
                message=message,
                require_confirmation=False,
            )

            if dialog.ShowModal() != wx.ID_OK:
                dialog.Destroy()
                return None

            password = dialog.GetPassword()
            dialog.Destroy()

            # Verify password by trying to decrypt first account
            if accounts_manager.verify_password(password):
                return password

            # If this was the last attempt, show error
            if attempt == max_attempts:
                wx.MessageBox(
                    (
                        "Maximum login attempts exceeded.\n\n"
                        "The application will now close."
                    ),
                    "Authentication Failed",
                    wx.OK | wx.ICON_ERROR,
                )

        return None


def main():
    """Launch the Simple OTP application."""
    app = wx.App()

    # Perform authentication
    password = authenticate()

    if password is None:
        # User cancelled or failed authentication
        return

    # Create and show main window with the validated password
    frame = MainWindow(None, password)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
