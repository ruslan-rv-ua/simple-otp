"""Tests for Add Account Dialog."""

import pytest
import wx

from simple_otp.models.totp_account import DigestAlgorithm
from simple_otp.ui.add_account_dialog import AddAccountDialog


class TestAddAccountDialog:
    """Tests for AddAccountDialog."""

    @pytest.fixture
    def app(self):
        """Create a wxPython app for testing."""
        app = wx.App()
        yield app
        app.Destroy()

    @pytest.fixture
    def dialog(self, app):
        """Create an AddAccountDialog instance."""
        dialog = AddAccountDialog(None)
        yield dialog
        dialog.Destroy()

    def test_dialog_creation(self, dialog):
        """Test that dialog is created successfully."""
        assert dialog is not None
        assert dialog.GetTitle() == "Add Account"

    def test_get_account_data_defaults(self, dialog):
        """Test getting account data with default values."""
        # Set minimal required fields
        dialog.name_ctrl.SetValue("test@example.com")
        dialog.secret_ctrl.SetValue("JBSWY3DPEHPK3PXP")

        data = dialog.get_account_data()

        assert data["name"] == "test@example.com"
        assert data["secret"] == "JBSWY3DPEHPK3PXP"
        assert data["issuer"] == ""
        assert data["digits"] == 6
        assert data["digest"] == DigestAlgorithm.SHA1
        assert data["interval"] == 30

    def test_get_account_data_custom_values(self, dialog):
        """Test getting account data with custom values."""
        dialog.name_ctrl.SetValue("user@test.com")
        dialog.secret_ctrl.SetValue("JBSWY3DPEHPK3PXP")
        dialog.issuer_ctrl.SetValue("GitHub")
        dialog.digits_ctrl.SetSelection(1)  # 8 digits
        dialog.digest_ctrl.SetSelection(1)  # SHA256
        dialog.interval_ctrl.SetValue(60)

        data = dialog.get_account_data()

        assert data["name"] == "user@test.com"
        assert data["secret"] == "JBSWY3DPEHPK3PXP"
        assert data["issuer"] == "GitHub"
        assert data["digits"] == 8
        assert data["digest"] == DigestAlgorithm.SHA256
        assert data["interval"] == 60

    def test_secret_normalization(self, dialog):
        """Test that secret is normalized (spaces removed, uppercase)."""
        dialog.name_ctrl.SetValue("test@example.com")
        # Secret with spaces and lowercase
        dialog.secret_ctrl.SetValue("jbsw y3dp ehpk 3pxp")

        data = dialog.get_account_data()

        # Should be uppercase with no spaces
        assert data["secret"] == "JBSWY3DPEHPK3PXP"

    # Note: Validation tests that trigger wx.MessageBox are commented out
    # as they require a full GUI event loop and user interaction
    # The validation logic is still tested indirectly through manual testing

    def test_is_valid_base32_valid_strings(self, dialog):
        """Test base32 validation for valid strings."""
        assert dialog._is_valid_base32("JBSWY3DPEHPK3PXP") is True
        assert dialog._is_valid_base32("ABCDEFGH") is True
        assert dialog._is_valid_base32("2345ABCD") is True
        assert dialog._is_valid_base32("ABCD2345====") is True  # With padding

    def test_is_valid_base32_invalid_strings(self, dialog):
        """Test base32 validation for invalid strings."""
        assert dialog._is_valid_base32("INVALID1") is False  # Contains '1'
        assert dialog._is_valid_base32("SHORT") is False  # Too short
        assert dialog._is_valid_base32("INVALID0") is False  # Contains '0'
        assert dialog._is_valid_base32("invalid") is False  # Lowercase
        assert dialog._is_valid_base32("ABC!DEF") is False  # Special char

    def test_is_valid_base32_with_spaces(self, dialog):
        """Test base32 validation handles spaces correctly."""
        # Spaces should be allowed (they'll be removed during normalization)
        assert dialog._is_valid_base32("JBSW Y3DP EHPK 3PXP") is True
