"""Tests for MainWindow."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import wx

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.core.settings_manager import SettingsManager
from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount
from simple_otp.ui.main_window import MainWindow


class TestMainWindow:
    """Tests for MainWindow."""

    @pytest.fixture
    def app(self):
        """Create a wxPython app for testing."""
        app = wx.App()
        yield app
        app.Destroy()

    @pytest.fixture
    def temp_settings(self):
        """Create a temporary settings file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = Path(f.name)
        if temp_file.exists():
            temp_file.unlink()
        settings_manager = SettingsManager(temp_file)
        yield settings_manager, temp_file
        if temp_file.exists():
            temp_file.unlink()

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
            name="test@example.com",
            secret="JBSWY3DPEHPK3PXP",
            password=password,
            issuer="Test",
            digits=6,
            digest=DigestAlgorithm.SHA1,
            interval=30,
        )
        accounts_manager.add_account(test_account)

        yield temp_file, password
        if temp_file.exists():
            temp_file.unlink()

    @pytest.fixture
    def main_window(self, app, temp_settings):
        """Create a MainWindow instance with mocked settings."""
        settings_manager, temp_file = temp_settings

        # Patch SettingsManager to return our test instance
        with patch(
            "simple_otp.ui.main_window.SettingsManager", return_value=settings_manager
        ):
            # Disable open last file on startup for most tests
            settings_manager.set("files.open_last_file_on_startup", False)
            settings_manager.save()

            window = MainWindow(None)
            yield window
            window.Destroy()

    def test_window_creation(self, main_window):
        """Test that main window is created successfully."""
        assert main_window is not None
        assert isinstance(main_window, wx.Frame)
        assert main_window.accounts_manager is None
        assert main_window.current_file is None
        assert main_window.password is None

    def test_authenticate_success(self, main_window, temp_accounts_file):
        """Test successful authentication via authenticator."""
        file_path, password = temp_accounts_file

        # Mock the PasswordDialog to return the correct password
        with patch("simple_otp.core.authenticator.PasswordDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.ShowModal.return_value = wx.ID_OK
            mock_dialog.GetPassword.return_value = password
            mock_dialog_class.return_value = mock_dialog

            accounts_manager, result_password = main_window.authenticator.authenticate(
                file_path
            )

            assert accounts_manager is not None
            assert result_password == password
            mock_dialog.Destroy.assert_called_once()

    def test_authenticate_cancelled(self, main_window, temp_accounts_file):
        """Test authentication cancelled by user."""
        file_path, _ = temp_accounts_file

        # Mock the PasswordDialog to return CANCEL
        with patch("simple_otp.core.authenticator.PasswordDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.ShowModal.return_value = wx.ID_CANCEL
            mock_dialog_class.return_value = mock_dialog

            accounts_manager, result_password = main_window.authenticator.authenticate(
                file_path
            )

            assert accounts_manager is None
            assert result_password is None
            mock_dialog.Destroy.assert_called_once()

    def test_authenticate_wrong_password(self, main_window, temp_accounts_file):
        """Test authentication with wrong password."""
        file_path, _ = temp_accounts_file

        # Mock the PasswordDialog to return wrong password 3 times
        with patch("simple_otp.core.authenticator.PasswordDialog") as mock_dialog_class:
            mock_dialog = MagicMock()
            mock_dialog.ShowModal.return_value = wx.ID_OK
            mock_dialog.GetPassword.return_value = "wrong_password"
            mock_dialog_class.return_value = mock_dialog

            # Mock MessageBox to avoid showing error dialog
            with patch("simple_otp.core.authenticator.wx.MessageBox"):
                accounts_manager, result_password = (
                    main_window.authenticator.authenticate(file_path)
                )

                assert accounts_manager is None
                assert result_password is None
                # Should be called 3 times (max attempts)
                assert mock_dialog.ShowModal.call_count == 3

    def test_open_last_file_on_startup_disabled(
        self, app, temp_settings, temp_accounts_file
    ):
        """Test that last file is not opened when setting is disabled."""
        settings_manager, temp_file = temp_settings
        accounts_file, password = temp_accounts_file

        # Disable open last file on startup
        settings_manager.set("files.open_last_file_on_startup", False)
        settings_manager.set("files.recent_files", [str(accounts_file)])
        settings_manager.save()

        with patch(
            "simple_otp.ui.main_window.SettingsManager", return_value=settings_manager
        ):
            window = MainWindow(None)

            # Window should have no file open
            assert window.accounts_manager is None
            assert window.current_file is None

            window.Destroy()

    def test_open_last_file_on_startup_no_recent_files(
        self, app, temp_settings, temp_accounts_file
    ):
        """Test startup with no recent files."""
        settings_manager, temp_file = temp_settings

        # Enable open last file but have no recent files
        settings_manager.set("files.open_last_file_on_startup", True)
        settings_manager.set("files.recent_files", [])
        settings_manager.save()

        with patch(
            "simple_otp.ui.main_window.SettingsManager", return_value=settings_manager
        ):
            window = MainWindow(None)

            # Window should have no file open
            assert window.accounts_manager is None
            assert window.current_file is None

            window.Destroy()

    def test_open_last_file_on_startup_file_not_exists(
        self, app, temp_settings, temp_accounts_file
    ):
        """Test startup when last file doesn't exist."""
        settings_manager, temp_file = temp_settings
        accounts_file, password = temp_accounts_file

        # Add a non-existent file to recent files
        non_existent = Path("c:/non_existent_file.json")
        settings_manager.set("files.open_last_file_on_startup", True)
        settings_manager.set("files.recent_files", [str(non_existent)])
        settings_manager.save()

        with patch(
            "simple_otp.ui.main_window.SettingsManager", return_value=settings_manager
        ):
            with patch(
                "simple_otp.core.recent_files_manager.SettingsManager",
                return_value=settings_manager,
            ):
                window = MainWindow(None)

                # Window should have no file open
                assert window.accounts_manager is None
                assert window.current_file is None

                # Non-existent file should be removed from recent files
                recent_files = window.recent_files_manager.get_recent_files_strings()
                assert str(non_existent.resolve()) not in recent_files

                window.Destroy()

    def test_open_last_file_on_startup_success(
        self, app, temp_settings, temp_accounts_file
    ):
        """Test successful opening of last file on startup."""
        settings_manager, temp_file = temp_settings
        accounts_file, password = temp_accounts_file

        # Enable open last file and add accounts file to recent files
        settings_manager.set("files.open_last_file_on_startup", True)
        settings_manager.set("files.recent_files", [str(accounts_file)])
        settings_manager.save()

        # Mock the PasswordDialog to return the correct password
        with patch(
            "simple_otp.ui.main_window.SettingsManager", return_value=settings_manager
        ):
            with patch(
                "simple_otp.core.recent_files_manager.SettingsManager",
                return_value=settings_manager,
            ):
                with patch(
                    "simple_otp.core.authenticator.PasswordDialog"
                ) as mock_dialog_class:
                    mock_dialog = MagicMock()
                    mock_dialog.ShowModal.return_value = wx.ID_OK
                    mock_dialog.GetPassword.return_value = password
                    mock_dialog_class.return_value = mock_dialog

                    window = MainWindow(None)

                    # Process pending events to execute wx.CallAfter
                    app.Yield()

                    # Window should have the file open
                    assert window.accounts_manager is not None
                    assert window.current_file == accounts_file
                    assert window.password == password

                    window.Destroy()

    def test_open_last_file_on_startup_cancelled(
        self, app, temp_settings, temp_accounts_file
    ):
        """Test when user cancels authentication on startup."""
        settings_manager, temp_file = temp_settings
        accounts_file, password = temp_accounts_file

        # Enable open last file
        settings_manager.set("files.open_last_file_on_startup", True)
        settings_manager.set("files.recent_files", [str(accounts_file)])
        settings_manager.save()

        # Mock the PasswordDialog to return CANCEL
        with patch(
            "simple_otp.ui.main_window.SettingsManager", return_value=settings_manager
        ):
            with patch(
                "simple_otp.core.recent_files_manager.SettingsManager",
                return_value=settings_manager,
            ):
                with patch(
                    "simple_otp.core.authenticator.PasswordDialog"
                ) as mock_dialog_class:
                    mock_dialog = MagicMock()
                    mock_dialog.ShowModal.return_value = wx.ID_CANCEL
                    mock_dialog_class.return_value = mock_dialog

                    window = MainWindow(None)

                    # Process pending events to execute wx.CallAfter
                    app.Yield()

                    # Window should have no file open
                    assert window.accounts_manager is None
                    assert window.current_file is None

                    window.Destroy()
