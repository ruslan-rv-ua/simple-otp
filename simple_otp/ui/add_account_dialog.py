"""Dialog for adding a new TOTP account."""

import base64
import re

import wx

from simple_otp.models.totp_account import DigestAlgorithm


class AddAccountDialog(wx.Dialog):
    """Dialog for adding a new TOTP account."""

    def __init__(self, parent):
        """
        Initialize the add account dialog.

        Args:
            parent: Parent window
        """
        super().__init__(
            parent,
            title="Add Account",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self._create_ui()
        self.Centre()

    def _create_ui(self):
        """Create the dialog UI."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Name field (required)
        name_label = wx.StaticText(panel, label="Name (e.g., user@example.com) *:")
        main_sizer.Add(name_label, 0, wx.ALL, 5)

        self.name_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        main_sizer.Add(self.name_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Secret field (required)
        secret_label = wx.StaticText(panel, label="Secret (Base32) *:")
        main_sizer.Add(secret_label, 0, wx.ALL, 5)

        self.secret_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        main_sizer.Add(self.secret_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Issuer field (optional)
        issuer_label = wx.StaticText(panel, label="Issuer (e.g., Google, GitHub):")
        main_sizer.Add(issuer_label, 0, wx.ALL, 5)

        self.issuer_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        main_sizer.Add(self.issuer_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Digits field (6 or 8)
        digits_label = wx.StaticText(panel, label="Digits:")
        main_sizer.Add(digits_label, 0, wx.ALL, 5)

        self.digits_ctrl = wx.Choice(panel, choices=["6", "8"])
        self.digits_ctrl.SetSelection(0)  # Default to 6
        main_sizer.Add(self.digits_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Digest algorithm field
        digest_label = wx.StaticText(panel, label="Digest Algorithm:")
        main_sizer.Add(digest_label, 0, wx.ALL, 5)

        self.digest_ctrl = wx.Choice(panel, choices=["SHA1", "SHA256", "SHA512"])
        self.digest_ctrl.SetSelection(0)  # Default to SHA1
        main_sizer.Add(self.digest_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Interval field (seconds)
        interval_label = wx.StaticText(panel, label="Interval (seconds):")
        main_sizer.Add(interval_label, 0, wx.ALL, 5)

        self.interval_ctrl = wx.SpinCtrl(panel, value="30", min=1, max=300, initial=30)
        main_sizer.Add(self.interval_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Required fields note
        note_label = wx.StaticText(panel, label="* Required fields")
        font = note_label.GetFont()
        font.PointSize = 8
        note_label.SetFont(font)
        main_sizer.Add(note_label, 0, wx.ALL, 5)

        # Buttons
        button_sizer = wx.StdDialogButtonSizer()

        ok_button = wx.Button(panel, wx.ID_OK, "Add")
        ok_button.SetDefault()
        button_sizer.AddButton(ok_button)

        cancel_button = wx.Button(panel, wx.ID_CANCEL)
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
                "Name is required.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            self.name_ctrl.SetFocus()
            return False

        # Check secret is not empty and is valid base32
        secret = self.secret_ctrl.GetValue().strip()
        if not secret:
            wx.MessageBox(
                "Secret is required.",
                "Validation Error",
                wx.OK | wx.ICON_ERROR,
            )
            self.secret_ctrl.SetFocus()
            return False

        # Validate base32 format
        if not self._is_valid_base32(secret):
            wx.MessageBox(
                "Secret must be a valid Base32 string (A-Z, 2-7, optional padding with '=').",
                "Validation Error",
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
                f"Invalid Base32 secret: {str(e)}",
                "Validation Error",
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
