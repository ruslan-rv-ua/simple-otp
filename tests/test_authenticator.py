"""Tests for Authenticator."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import wx

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.core.authenticator import Authenticator
from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount


class TestAuthenticator:
    """Tests for Authenticator."""

    @pytest.fixture
    def app(self):
        """Create a wxPython app for testing."""
        app = wx.App()
        yield app
        app.Destroy()

    @pytest.fixture
    def parent_window(self, app):
        """Create a parent window for testing."""
        window = wx.Frame(None)
        yield window
        window.Destroy()

    @pytest.fixture
    def temp_accounts_file(self):
        """Create a temporary accounts file with test account."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = Path(f.name)
            # Write empty JSON structure
            f.write('{"accounts": []}')

        # Create accounts file with test account
        password = "test_password"
        accounts_manager = AccountsManager(storage_path=temp_file, auto_create=False)

        test_account = TOTPAccount.from_secret(
            name="Test Account",
            secret="JBSWY3DPEHPK3PXP",
            password=password,
            issuer="Test Issuer",
            digits=6,
            digest=DigestAlgorithm.SHA1,
            interval=30,
        )

        accounts_manager.add_account(test_account)

        yield temp_file, password

        # Cleanup
        if temp_file.exists():
            temp_file.unlink()

    def test_authenticate_success(self, app, parent_window, temp_accounts_file):
        """Test successful authentication."""
        file_path, password = temp_accounts_file
        authenticator = Authenticator(parent_window)

        # Mock the password dialog to return the correct password
        with patch("simple_otp.core.authenticator.PasswordDialog") as mock_dialog:
            mock_instance = MagicMock()
            mock_instance.ShowModal.return_value = wx.ID_OK
            mock_instance.GetPassword.return_value = password
            mock_dialog.return_value = mock_instance

            manager, returned_password = authenticator.authenticate(file_path)

            assert manager is not None
            assert returned_password == password
            assert isinstance(manager, AccountsManager)

    def test_authenticate_wrong_password(self, app, parent_window, temp_accounts_file):
        """Test authentication with wrong password."""
        file_path, _ = temp_accounts_file
        authenticator = Authenticator(parent_window)

        # Mock the password dialog to return wrong password
        with patch("simple_otp.core.authenticator.PasswordDialog") as mock_dialog:
            mock_instance = MagicMock()
            mock_instance.ShowModal.return_value = wx.ID_OK
            mock_instance.GetPassword.return_value = "wrong_password"
            mock_dialog.return_value = mock_instance

            # Mock MessageBox to avoid showing error dialog
            with patch("simple_otp.core.authenticator.wx.MessageBox"):
                manager, returned_password = authenticator.authenticate(
                    file_path, max_attempts=3
                )

                assert manager is None
                assert returned_password is None
                # Should try 3 times
                assert mock_dialog.call_count == 3

    def test_authenticate_cancelled(self, app, parent_window, temp_accounts_file):
        """Test authentication when user cancels."""
        file_path, _ = temp_accounts_file
        authenticator = Authenticator(parent_window)

        # Mock the password dialog to simulate user cancelling
        with patch("simple_otp.core.authenticator.PasswordDialog") as mock_dialog:
            mock_instance = MagicMock()
            mock_instance.ShowModal.return_value = wx.ID_CANCEL
            mock_dialog.return_value = mock_instance

            manager, returned_password = authenticator.authenticate(file_path)

            assert manager is None
            assert returned_password is None
            # Should only show dialog once before cancelling
            assert mock_dialog.call_count == 1

    def test_authenticate_file_not_found(self, app, parent_window):
        """Test authentication with non-existent file."""
        file_path = Path("non_existent_file.json")
        authenticator = Authenticator(parent_window)

        # AccountsManager will be created successfully, but verify_password will fail
        # because the file doesn't exist yet. Mock dialog and MessageBox.
        with patch("simple_otp.core.authenticator.PasswordDialog") as mock_dialog:
            mock_instance = MagicMock()
            mock_instance.ShowModal.return_value = wx.ID_OK
            mock_instance.GetPassword.return_value = "any_password"
            mock_dialog.return_value = mock_instance

            with patch("simple_otp.core.authenticator.wx.MessageBox"):
                manager, password = authenticator.authenticate(file_path)
                # Should fail because file doesn't exist for password verification
                assert manager is None
                assert password is None

    def test_authenticate_retry_then_success(
        self, app, parent_window, temp_accounts_file
    ):
        """Test authentication with wrong password then correct password."""
        file_path, password = temp_accounts_file
        authenticator = Authenticator(parent_window)

        # Mock the password dialog to return wrong password first, then correct
        with patch("simple_otp.core.authenticator.PasswordDialog") as mock_dialog:
            mock_instance = MagicMock()
            mock_instance.ShowModal.return_value = wx.ID_OK
            # First call: wrong password, second call: correct password
            mock_instance.GetPassword.side_effect = ["wrong_password", password]
            mock_dialog.return_value = mock_instance

            # Mock MessageBox to avoid showing error dialog
            with patch("simple_otp.core.authenticator.wx.MessageBox"):
                manager, returned_password = authenticator.authenticate(
                    file_path, max_attempts=3
                )

                assert manager is not None
                assert returned_password == password
                # Should try 2 times
                assert mock_dialog.call_count == 2
