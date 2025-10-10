"""File operations controller for MainWindow."""

import json
from pathlib import Path

import wx

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.core.authenticator import Authenticator
from simple_otp.core.i18n import _
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
        # Show file dialog
        with wx.FileDialog(
            self.parent,
            _("main.dialogs.create_new_file"),
            wildcard=_("main.dialogs.file_filter"),
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return None, None, None

            file_path = Path(file_dialog.GetPath())

            # Ensure .json extension
            if file_path.suffix.lower() != ".json":
                file_path = file_path.with_suffix(".json")

        # Ask for password with confirmation
        password_dialog = PasswordDialog(
            self.parent,
            title=_("password_dialog.title_set"),
            message=_("password_dialog.message_set"),
            require_confirmation=True,
        )

        if password_dialog.ShowModal() != wx.ID_OK:
            password_dialog.Destroy()
            return None, None, None

        new_password = password_dialog.GetPassword()
        password_dialog.Destroy()

        try:
            # Create an empty accounts file
            data = {"accounts": []}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Create new accounts manager with the file (auto_create=False)
            new_manager = AccountsManager(storage_path=file_path, auto_create=False)

            # Create the default account with the provided password
            new_manager.create_initial_account(new_password)

            return file_path, new_manager, new_password

        except Exception as e:
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
        # Show file dialog if path not provided
        if file_path is None:
            with wx.FileDialog(
                self.parent,
                _("main.dialogs.open_file"),
                wildcard=_("main.dialogs.file_filter"),
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            ) as file_dialog:
                if file_dialog.ShowModal() == wx.ID_CANCEL:
                    return None, None, None

                file_path = Path(file_dialog.GetPath())

        # Check if file exists
        if not file_path.exists():
            self._show_warning(
                _("main.messages.file_not_found", path=file_path),
                _("main.dialogs.file_not_found"),
            )
            return None, None, None

        # Authenticate
        accounts_manager, password = self.authenticator.authenticate(file_path)

        if accounts_manager and password:
            return file_path, accounts_manager, password

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
