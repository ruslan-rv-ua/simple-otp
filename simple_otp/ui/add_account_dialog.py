"""Dialog for adding a new TOTP account."""

import base64
import re

import wx

from simple_otp.core.i18n import _
from simple_otp.core.settings_manager import SettingsManager
from simple_otp.models.totp_account import DigestAlgorithm


class AddAccountDialog(wx.Dialog):
    """Dialog for adding a new TOTP account."""

    def __init__(self, parent, settings_manager: SettingsManager):
        """
        Initialize the add account dialog.

        Args:
            parent: Parent window
            settings_manager: SettingsManager instance for loading TOTP defaults
        """
        super().__init__(
            parent,
            title=_("add_account.title"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.settings_manager = settings_manager
        self._create_ui()
        self.CenterOnParent()

    def _create_ui(self):
        """Create the dialog UI."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Name field (required)
        name_label = wx.StaticText(panel, label=_("add_account.name_label"))
        main_sizer.Add(name_label, 0, wx.ALL, 5)

        self.name_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        main_sizer.Add(self.name_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Secret field (required)
        secret_label = wx.StaticText(panel, label=_("add_account.secret_label"))
        main_sizer.Add(secret_label, 0, wx.ALL, 5)

        self.secret_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        main_sizer.Add(self.secret_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Issuer field (optional)
        issuer_label = wx.StaticText(panel, label=_("add_account.issuer_label"))
        main_sizer.Add(issuer_label, 0, wx.ALL, 5)

        self.issuer_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        main_sizer.Add(self.issuer_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Digits field (6, 7, or 8)
        digits_label = wx.StaticText(panel, label=_("add_account.digits_label"))
        main_sizer.Add(digits_label, 0, wx.ALL, 5)

        self.digits_ctrl = wx.Choice(panel, choices=["6", "7", "8"])
        # Get default from settings
        default_digits = self.settings_manager.get("totp.default_digits", 6)
        self.digits_ctrl.SetSelection(default_digits - 6)  # 6->0, 7->1, 8->2
        main_sizer.Add(self.digits_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Digest algorithm field
        digest_label = wx.StaticText(panel, label=_("add_account.digest_label"))
        main_sizer.Add(digest_label, 0, wx.ALL, 5)

        self.digest_ctrl = wx.Choice(panel, choices=["SHA1", "SHA256", "SHA512"])
        # Get default from settings
        default_digest = self.settings_manager.get("totp.default_digest", "SHA1")
        digest_map = {"SHA1": 0, "SHA256": 1, "SHA512": 2}
        self.digest_ctrl.SetSelection(digest_map.get(default_digest, 0))
        main_sizer.Add(self.digest_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Interval field (seconds)
        interval_label = wx.StaticText(panel, label=_("add_account.interval_label"))
        main_sizer.Add(interval_label, 0, wx.ALL, 5)

        # Get default from settings
        default_interval = self.settings_manager.get("totp.default_interval", 30)
        self.interval_ctrl = wx.SpinCtrl(
            panel, value=str(default_interval), min=1, max=300, initial=default_interval
        )
        main_sizer.Add(self.interval_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Required fields note
        note_label = wx.StaticText(panel, label=_("add_account.required_note"))
        font = note_label.GetFont()
        font.PointSize = 8
        note_label.SetFont(font)
        main_sizer.Add(note_label, 0, wx.ALL, 5)

        # Buttons
        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(panel, wx.ID_OK, _("add_account.button_add"))
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(panel, wx.ID_CANCEL, _("add_account.button_cancel"))
        button_sizer.AddButton(cancel_button)

        button_sizer.Realize()
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        # Bind OK button
        ok_button.Bind(wx.EVT_BUTTON, self._on_ok)

        panel.SetSizer(main_sizer)
        main_sizer.Fit(self)

        # Set minimum size
        self.SetMinSize(wx.Size(400, -1))

        # Focus on name field
        self.name_ctrl.SetFocus()

    def _on_ok(self, event):
        """Handle OK button click with validation."""
        # Validate the input
        if not self._validate_input():
            return

        # End the dialog with OK result
        self.EndModal(wx.ID_OK)

    def _validate_input(self) -> bool:
        """
        Validate the user input.

        Returns:
            True if all input is valid, False otherwise
        """
        # Check name is not empty
        name = self.name_ctrl.GetValue().strip()
        if not name:
            wx.MessageBox(
                _("add_account.validation.name_required"),
                _("add_account.validation.validation_error"),
                wx.OK | wx.ICON_ERROR,
            )
            self.name_ctrl.SetFocus()
            return False

        # Check secret is not empty and is valid base32
        secret = self.secret_ctrl.GetValue().strip()
        if not secret:
            wx.MessageBox(
                _("add_account.validation.secret_required"),
                _("add_account.validation.validation_error"),
                wx.OK | wx.ICON_ERROR,
            )
            self.secret_ctrl.SetFocus()
            return False

        # Validate base32 format
        if not self._is_valid_base32(secret):
            wx.MessageBox(
                _("add_account.validation.invalid_base32"),
                _("add_account.validation.validation_error"),
                wx.OK | wx.ICON_ERROR,
            )
            self.secret_ctrl.SetFocus()
            return False

        # Try to decode the secret to ensure it's valid
        try:
            # Remove spaces and convert to uppercase for decoding
            clean_secret = secret.replace(" ", "").upper()
            base64.b32decode(clean_secret)
        except Exception as e:
            wx.MessageBox(
                _("add_account.validation.invalid_base32_decode", error=str(e)),
                _("add_account.validation.validation_error"),
                wx.OK | wx.ICON_ERROR,
            )
            self.secret_ctrl.SetFocus()
            return False

        return True

    def _is_valid_base32(self, value: str) -> bool:
        """
        Check if a string is valid Base32 format.

        Args:
            value: String to validate

        Returns:
            True if valid Base32, False otherwise
        """
        # Remove spaces for validation
        clean_value = value.replace(" ", "").upper()

        # Base32 uses A-Z and 2-7, with optional padding '='
        # Must be at least 8 characters (or multiple of 8 with padding)
        pattern = r"^[A-Z2-7]+=*$"

        if not re.match(pattern, clean_value):
            return False

        # Check length - base32 should be multiple of 8 (with or without padding)
        # But we'll be lenient here since padding might be optional
        return len(clean_value) >= 8

    def get_account_data(self) -> dict:
        """
        Get the account data from the dialog fields.

        Returns:
            Dictionary with account parameters
        """
        # Get digest algorithm
        digest_choice = self.digest_ctrl.GetSelection()
        digest_map = {
            0: DigestAlgorithm.SHA1,
            1: DigestAlgorithm.SHA256,
            2: DigestAlgorithm.SHA512,
        }

        # Clean and normalize the secret (remove spaces, convert to uppercase)
        secret = self.secret_ctrl.GetValue().strip().replace(" ", "").upper()

        return {
            "name": self.name_ctrl.GetValue().strip(),
            "secret": secret,
            "issuer": self.issuer_ctrl.GetValue().strip(),
            "digits": int(self.digits_ctrl.GetString(self.digits_ctrl.GetSelection())),
            "digest": digest_map[digest_choice],
            "interval": self.interval_ctrl.GetValue(),
        }
