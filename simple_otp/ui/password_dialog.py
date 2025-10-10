"""Password entry dialog for authentication and initial setup."""

import wx

from simple_otp.core.i18n import _


class PasswordDialog(wx.Dialog):
    """
    Dialog for password entry with optional confirmation field.

    Used for both initial setup (with confirmation) and login (without confirmation).
    """

    def __init__(
        self,
        parent,
        title: str | None = None,
        message: str | None = None,
        require_confirmation: bool = False,
    ):
        """
        Initialize the password dialog.

        Args:
            parent: Parent window
            title: Dialog title
            message: Message to display above password field
            require_confirmation: If True, show password confirmation field
        """
        # Use default title and message if not provided
        if title is None:
            title = _("password_dialog.title_required")
        if message is None:
            message = _("password_dialog.message_enter")

        super().__init__(parent, title=title, style=wx.DEFAULT_DIALOG_STYLE)

        self.require_confirmation = require_confirmation
        self._create_ui(message)

        # Center the dialog
        self.Centre()

    def _create_ui(self, message: str):
        """Create the dialog UI."""
        # Main sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Message (only if not empty)
        if message:
            message_text = wx.StaticText(self, label=message)
            sizer.Add(message_text, 0, wx.ALL | wx.EXPAND, 10)

        # Password field
        password_label = wx.StaticText(self, label=_("password_dialog.password_label"))
        sizer.Add(password_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        self.password_ctrl = wx.TextCtrl(
            self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER
        )
        sizer.Add(self.password_ctrl, 0, wx.ALL | wx.EXPAND, 10)

        # Confirmation field (if required)
        if self.require_confirmation:
            confirm_label = wx.StaticText(
                self, label=_("password_dialog.confirm_label")
            )
            sizer.Add(confirm_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

            self.confirm_ctrl = wx.TextCtrl(
                self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER
            )
            sizer.Add(self.confirm_ctrl, 0, wx.ALL | wx.EXPAND, 10)

            # Bind Enter key on confirmation field
            self.confirm_ctrl.Bind(wx.EVT_TEXT_ENTER, self._on_ok)
        else:
            self.confirm_ctrl = None

            # Bind Enter key on password field
            self.password_ctrl.Bind(wx.EVT_TEXT_ENTER, self._on_ok)

        # Buttons
        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(self, wx.ID_OK)
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(self, wx.ID_CANCEL)
        button_sizer.AddButton(cancel_button)

        button_sizer.Realize()
        sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        # Bind OK button
        ok_button.Bind(wx.EVT_BUTTON, self._on_ok)

        self.SetSizer(sizer)
        self.Fit()

        # Set minimum size
        self.SetMinSize(wx.Size(350, -1))

        # Focus on password field
        self.password_ctrl.SetFocus()

    def _on_ok(self, event):
        """Handle OK button click."""
        password = self.password_ctrl.GetValue()

        # Validate password is not empty
        if not password:
            wx.MessageBox(
                _("password_dialog.validation.password_empty"),
                _("password_dialog.validation.invalid_password"),
                wx.OK | wx.ICON_WARNING,
                self,
            )
            self.password_ctrl.SetFocus()
            return

        # If confirmation is required, validate it matches
        if self.require_confirmation and self.confirm_ctrl is not None:
            confirm = self.confirm_ctrl.GetValue()
            if password != confirm:
                wx.MessageBox(
                    _("password_dialog.validation.passwords_mismatch"),
                    _("password_dialog.validation.password_mismatch"),
                    wx.OK | wx.ICON_WARNING,
                    self,
                )
                self.confirm_ctrl.SetValue("")
                self.confirm_ctrl.SetFocus()
                return

        # Close with OK result
        self.EndModal(wx.ID_OK)

    def GetPassword(self) -> str:
        """
        Get the entered password.

        Returns:
            The password entered by the user
        """
        return self.password_ctrl.GetValue()
