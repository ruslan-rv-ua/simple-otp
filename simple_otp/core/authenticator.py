"""Authentication handler for accounts files."""

from pathlib import Path

import wx

from simple_otp.constants import MAX_PASSWORD_ATTEMPTS
from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.core.i18n import _
from simple_otp.core.logger import logger
from simple_otp.ui.password_dialog import PasswordDialog


class Authenticator:
    """Handles password authentication for accounts files."""

    def __init__(self, parent_window: wx.Window):
        """
        Initialize the authenticator.

        Args:
            parent_window: Parent window for displaying dialogs
        """
        logger.debug("Authenticator initialized")
        self.parent = parent_window

    def authenticate(
        self, file_path: Path, max_attempts: int = MAX_PASSWORD_ATTEMPTS
    ) -> tuple[AccountsManager | None, str | None]:
        """
        Authenticate and create an AccountsManager for a specific file.

        Shows a password dialog with up to max_attempts attempts.
        On successful authentication, returns both the manager and password.

        Args:
            file_path: Path to the accounts file to authenticate against
            max_attempts: Maximum number of password attempts

        Returns:
            Tuple of (accounts_manager, password):
                - accounts_manager: Initialized and verified manager, or None
                - password: The validated password, or None if cancelled/failed

        Raises:
            FileNotFoundError: If the accounts file doesn't exist
        """
        logger.info(f"Authentication requested for file: {file_path}")
        logger.debug(f"Max authentication attempts: {max_attempts}")

        try:
            # Create accounts manager for the specific file
            accounts_manager = AccountsManager(
                storage_path=file_path, auto_create=False
            )
            logger.debug("AccountsManager created successfully")
        except FileNotFoundError:
            logger.error(f"File not found for authentication: {file_path}")
            raise
        except Exception as e:
            logger.opt(exception=True).error(
                f"Failed to create AccountsManager for {file_path}: {e}"
            )
            self._show_error(_("main.messages.failed_to_open_file", error=str(e)))
            return None, None

        # Request and verify password
        password = self._request_password_with_retry(
            file_path, accounts_manager, max_attempts
        )

        if password:
            logger.info(f"Authentication successful for: {file_path}")
            return accounts_manager, password

        logger.warning(f"Authentication failed for: {file_path}")
        return None, None

    def _request_password_with_retry(
        self, file_path: Path, accounts_manager: AccountsManager, max_attempts: int
    ) -> str | None:
        """
        Request password with multiple retry attempts.

        Args:
            file_path: Path to the accounts file (for display in dialog)
            accounts_manager: Manager instance to verify password against
            max_attempts: Maximum number of password attempts

        Returns:
            Validated password string, or None if cancelled or max attempts exceeded
        """
        logger.debug(f"Starting password retry loop (max {max_attempts} attempts)")

        for attempt in range(1, max_attempts + 1):
            remaining = max_attempts - attempt + 1
            logger.debug(f"Password attempt {attempt}/{max_attempts}")

            # Generate dialog title based on attempt number
            if attempt == 1:
                dialog_title = _(
                    "authentication.enter_password", filename=file_path.name
                )
            else:
                logger.info(
                    f"Previous password incorrect, attempt {attempt}/{max_attempts}"
                )
                dialog_title = _(
                    "authentication.incorrect_password",
                    remaining=remaining,
                    filename=file_path.name,
                )

            # Show password dialog
            logger.debug("Showing password dialog")
            dialog = PasswordDialog(
                self.parent,
                title=dialog_title,
                message="",
                require_confirmation=False,
            )

            if dialog.ShowModal() != wx.ID_OK:
                dialog.Destroy()
                logger.info("User cancelled password entry")
                return None  # User cancelled

            password = dialog.GetPassword()
            dialog.Destroy()
            logger.debug("Password entered by user")

            # Verify password
            try:
                logger.debug("Verifying password")
                if accounts_manager.verify_password(password):
                    logger.info("Password verified successfully")
                    return password
                else:
                    logger.warning("Password verification failed (incorrect password)")
            except Exception as e:
                logger.opt(exception=True).error(f"Password verification error: {e}")
                self._show_error(
                    _("main.messages.password_verification_failed", error=str(e))
                )
                return None

        # Max attempts exceeded
        logger.warning(
            f"Maximum password attempts ({max_attempts}) exceeded for {file_path}"
        )
        return None

    def _show_error(self, message: str):
        """
        Show error message box.

        Args:
            message: Error message to display
        """
        wx.MessageBox(
            message,
            _("main.dialogs.error"),
            wx.OK | wx.ICON_ERROR,
        )
