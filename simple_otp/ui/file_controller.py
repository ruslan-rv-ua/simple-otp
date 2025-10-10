"""File operations controller for MainWindow."""

import json
from pathlib import Path

import wx

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.core.authenticator import Authenticator
from simple_otp.core.i18n import _
from simple_otp.core.logger import logger
from simple_otp.ui.password_dialog import PasswordDialog


class FileController:
    """Handles file operations for MainWindow."""

    def __init__(self, parent_window: wx.Window, authenticator: Authenticator):
        """
        Initialize the file controller.

        Args:
            parent_window: Parent window for displaying dialogs
            authenticator: Authenticator instance for password handling
        """
        logger.debug("FileController initialized")
        self.parent = parent_window
        self.authenticator = authenticator

    def create_new_file(
        self,
    ) -> tuple[Path | None, AccountsManager | None, str | None]:
        """
        Handle new file creation with user dialogs.

        Shows file dialog for path selection and password dialog for
        setting the file password. Creates empty accounts file and
        initializes it with a default account.

        Returns:
            Tuple of (file_path, accounts_manager, password):
                - file_path: Path to the created file, or None if cancelled
                - accounts_manager: Initialized manager, or None if failed
                - password: The set password, or None if cancelled/failed
        """
        logger.info("User initiated new file creation")

        # Show file dialog
        logger.debug("Showing file save dialog")
        with wx.FileDialog(
            self.parent,
            _("main.dialogs.create_new_file"),
            wildcard=_("main.dialogs.file_filter"),
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                logger.info("User cancelled new file creation (file dialog)")
                return None, None, None

            file_path = Path(file_dialog.GetPath())
            logger.debug(f"User selected file path: {file_path}")

            # Ensure .json extension
            if file_path.suffix.lower() != ".json":
                original_path = file_path
                file_path = file_path.with_suffix(".json")
                logger.debug(f"Added .json extension: {original_path} -> {file_path}")

        # Ask for password with confirmation
        logger.debug("Showing password setup dialog")
        password_dialog = PasswordDialog(
            self.parent,
            title=_("password_dialog.title_set"),
            message=_("password_dialog.message_set"),
            require_confirmation=True,
        )

        if password_dialog.ShowModal() != wx.ID_OK:
            password_dialog.Destroy()
            logger.info("User cancelled new file creation (password dialog)")
            return None, None, None

        new_password = password_dialog.GetPassword()
        password_dialog.Destroy()
        logger.debug("Password set by user")

        try:
            logger.info(f"Creating new accounts file: {file_path}")
            # Create an empty accounts file
            data = {"accounts": []}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Empty JSON file created: {file_path}")

            # Create new accounts manager with the file (auto_create=False)
            new_manager = AccountsManager(storage_path=file_path, auto_create=False)
            logger.debug("AccountsManager created for new file")

            # Create the default account with the provided password
            logger.debug("Creating initial account")
            new_manager.create_initial_account(new_password)

            logger.info(f"New file created successfully: {file_path}")
            return file_path, new_manager, new_password

        except Exception as e:
            logger.opt(exception=True).error(f"Failed to create new file: {e}")
            self._show_error(_("main.messages.failed_to_open_file", error=str(e)))
            return None, None, None

    def open_file(
        self, file_path: Path | None = None
    ) -> tuple[Path | None, AccountsManager | None, str | None]:
        """
        Handle file opening with optional path.

        If file_path is not provided, shows file dialog for selection.
        Authenticates the user and returns the manager and password.

        Args:
            file_path: Optional path to the file to open.
                      If None, shows file dialog.

        Returns:
            Tuple of (file_path, accounts_manager, password):
                - file_path: Path to the opened file, or None if cancelled
                - accounts_manager: Authenticated manager, or None if failed
                - password: The validated password, or None if cancelled/failed
        """
        logger.info("User initiated file open")

        # Show file dialog if path not provided
        if file_path is None:
            logger.debug("Showing file open dialog")
            with wx.FileDialog(
                self.parent,
                _("main.dialogs.open_file"),
                wildcard=_("main.dialogs.file_filter"),
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            ) as file_dialog:
                if file_dialog.ShowModal() == wx.ID_CANCEL:
                    logger.info("User cancelled file open (file dialog)")
                    return None, None, None

                file_path = Path(file_dialog.GetPath())
                logger.debug(f"User selected file: {file_path}")
        else:
            logger.debug(f"Opening specified file: {file_path}")

        # Check if file exists
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            self._show_warning(
                _("main.messages.file_not_found", path=file_path),
                _("main.dialogs.file_not_found"),
            )
            return None, None, None

        # Authenticate
        logger.info(f"Attempting to open file: {file_path}")
        accounts_manager, password = self.authenticator.authenticate(file_path)

        if accounts_manager and password:
            logger.info(f"File opened successfully: {file_path}")
            return file_path, accounts_manager, password

        logger.warning(f"Failed to open file (authentication failed): {file_path}")
        return None, None, None

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

    def _show_warning(self, message: str, title: str):
        """
        Show warning message box.

        Args:
            message: Warning message to display
            title: Dialog title
        """
        wx.MessageBox(
            message,
            title,
            wx.OK | wx.ICON_WARNING,
        )
