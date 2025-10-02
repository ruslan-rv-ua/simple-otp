"""Tests for TOTP Dialog."""

import pytest
import wx

from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount
from simple_otp.ui.totp_dialog import TOTPDialog, format_otp


class TestTOTPDialog:
    """Tests for TOTPDialog."""

    @pytest.fixture
    def app(self):
        """Create a wxPython app for testing."""
        app = wx.App()
        yield app
        app.Destroy()

    @pytest.fixture
    def account(self):
        """Create a test TOTP account."""
        return TOTPAccount.from_secret(
            name="test@example.com",
            secret="JBSWY3DPEHPK3PXP",
            password="demo123",
            issuer="Test Service",
            digits=6,
            digest=DigestAlgorithm.SHA1,
            interval=30,
        )

    @pytest.fixture
    def dialog(self, app, account):
        """Create a TOTPDialog instance."""
        dialog = TOTPDialog(None, account, "demo123")
        yield dialog
        dialog.Destroy()

    def test_format_otp(self):
        """Test OTP formatting function."""
        # Test 6-digit code
        assert format_otp("123456") == "12 34 56"

        # Test 8-digit code
        assert format_otp("12345678") == "12 34 56 78"

    def test_dialog_creation(self, dialog, account):
        """Test that dialog is created successfully."""
        assert dialog is not None
        assert dialog.GetTitle() == f"TOTP - {account.get_display_name()}"
        assert dialog.account == account
        assert dialog.password == "demo123"

    def test_update_codes_and_progress(self, dialog):
        """Test that codes and progress are updated correctly."""
        # Call the update method
        dialog._update_codes_and_progress()

        # Check that current and next codes are set (should be non-empty strings)
        current_code = dialog.current_text.GetValue()
        next_code = dialog.next_text.GetValue()

        assert len(current_code) > 0
        assert len(next_code) > 0

        # Check that codes are formatted with spaces
        assert " " in current_code
        assert " " in next_code

        # Check that progress bar has a value between 0 and 100
        progress = dialog.progress_bar.GetValue()
        assert 0 <= progress <= 100

    def test_copy_current_button(self, dialog, monkeypatch):
        """Test copying current OTP to clipboard."""
        import pyperclip

        # Mock pyperclip.copy to verify it's called
        copied_text = []
        original_copy = pyperclip.copy

        def mock_copy(text):
            copied_text.append(text)
            return original_copy(text)

        monkeypatch.setattr(pyperclip, "copy", mock_copy)

        # Simulate button click
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, dialog.current_copy_btn.GetId())
        dialog._on_copy_current(event)

        # Verify that the current code (without spaces) was copied
        assert len(copied_text) == 1
        current_code = dialog.current_text.GetValue().replace(" ", "")
        assert copied_text[0] == current_code

    def test_copy_next_button(self, dialog, monkeypatch):
        """Test copying next OTP to clipboard."""
        import pyperclip

        # Mock pyperclip.copy to verify it's called
        copied_text = []
        original_copy = pyperclip.copy

        def mock_copy(text):
            copied_text.append(text)
            return original_copy(text)

        monkeypatch.setattr(pyperclip, "copy", mock_copy)

        # Simulate button click
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, dialog.next_copy_btn.GetId())
        dialog._on_copy_next(event)

        # Verify that the next code (without spaces) was copied
        assert len(copied_text) == 1
        next_code = dialog.next_text.GetValue().replace(" ", "")
        assert copied_text[0] == next_code


if __name__ == "__main__":
    pytest.main([__file__])
