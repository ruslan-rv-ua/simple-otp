"""Tests for FileController."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import wx

from simple_otp.core.authenticator import Authenticator
from simple_otp.ui.file_controller import FileController


class TestFileController:
    """Tests for FileController."""

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
    def authenticator(self, parent_window):
        """Create an authenticator instance."""
        return Authenticator(parent_window)

    @pytest.fixture
    def controller(self, parent_window, authenticator):
        """Create a file controller instance."""
        return FileController(parent_window, authenticator)

    def test_create_new_file_success(self, app, controller):
        """Test successful new file creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "test_accounts.json"

            # Mock file dialog
            with patch("simple_otp.ui.file_controller.wx.FileDialog") as mock_dialog:
                mock_dialog_instance = MagicMock()
                mock_dialog_instance.ShowModal.return_value = wx.ID_OK
                mock_dialog_instance.GetPath.return_value = str(temp_path)
                mock_dialog_instance.__enter__.return_value = mock_dialog_instance
                mock_dialog_instance.__exit__.return_value = None
                mock_dialog.return_value = mock_dialog_instance

                # Mock password dialog
                with patch(
                    "simple_otp.ui.file_controller.PasswordDialog"
                ) as mock_pass_dialog:
                    mock_pass_instance = MagicMock()
                    mock_pass_instance.ShowModal.return_value = wx.ID_OK
                    mock_pass_instance.GetPassword.return_value = "test_password"
                    mock_pass_dialog.return_value = mock_pass_instance

                    file_path, manager, password = controller.create_new_file()

                    assert file_path == temp_path
                    assert manager is not None
                    assert password == "test_password"
                    assert temp_path.exists()

                    # Verify file has correct structure
                    accounts = manager.list_accounts()
                    assert len(accounts) >= 1  # Should have initial account

    def test_create_new_file_cancelled_file_dialog(self, app, controller):
        """Test new file creation cancelled at file dialog."""
        # Mock file dialog to return CANCEL
        with patch("simple_otp.ui.file_controller.wx.FileDialog") as mock_dialog:
            mock_dialog_instance = MagicMock()
            mock_dialog_instance.ShowModal.return_value = wx.ID_CANCEL
            mock_dialog_instance.__enter__.return_value = mock_dialog_instance
            mock_dialog_instance.__exit__.return_value = None
            mock_dialog.return_value = mock_dialog_instance

            file_path, manager, password = controller.create_new_file()

            assert file_path is None
            assert manager is None
            assert password is None

    def test_create_new_file_cancelled_password_dialog(self, app, controller):
        """Test new file creation cancelled at password dialog."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path = Path(tmpdir) / "test_accounts.json"

            # Mock file dialog
            with patch("simple_otp.ui.file_controller.wx.FileDialog") as mock_dialog:
                mock_dialog_instance = MagicMock()
                mock_dialog_instance.ShowModal.return_value = wx.ID_OK
                mock_dialog_instance.GetPath.return_value = str(temp_path)
                mock_dialog_instance.__enter__.return_value = mock_dialog_instance
                mock_dialog_instance.__exit__.return_value = None
                mock_dialog.return_value = mock_dialog_instance

                # Mock password dialog to return CANCEL
                with patch(
                    "simple_otp.ui.file_controller.PasswordDialog"
                ) as mock_pass_dialog:
                    mock_pass_instance = MagicMock()
                    mock_pass_instance.ShowModal.return_value = wx.ID_CANCEL
                    mock_pass_dialog.return_value = mock_pass_instance

                    file_path, manager, password = controller.create_new_file()

                    assert file_path is None
                    assert manager is None
                    assert password is None

    def test_create_new_file_adds_json_extension(self, app, controller):
        """Test that .json extension is added if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_path_no_ext = Path(tmpdir) / "test_accounts"
            expected_path = Path(tmpdir) / "test_accounts.json"

            # Mock file dialog
            with patch("simple_otp.ui.file_controller.wx.FileDialog") as mock_dialog:
                mock_dialog_instance = MagicMock()
                mock_dialog_instance.ShowModal.return_value = wx.ID_OK
                mock_dialog_instance.GetPath.return_value = str(temp_path_no_ext)
                mock_dialog_instance.__enter__.return_value = mock_dialog_instance
                mock_dialog_instance.__exit__.return_value = None
                mock_dialog.return_value = mock_dialog_instance

                # Mock password dialog
                with patch(
                    "simple_otp.ui.file_controller.PasswordDialog"
                ) as mock_pass_dialog:
                    mock_pass_instance = MagicMock()
                    mock_pass_instance.ShowModal.return_value = wx.ID_OK
                    mock_pass_instance.GetPassword.return_value = "test_password"
                    mock_pass_dialog.return_value = mock_pass_instance

                    file_path, manager, password = controller.create_new_file()

                    assert file_path == expected_path
                    assert expected_path.exists()

    def test_open_file_with_dialog_success(self, app, controller):
        """Test opening file with file dialog."""
        # Create a temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write('{"accounts": []}')

        try:
            # Mock file dialog
            with patch("simple_otp.ui.file_controller.wx.FileDialog") as mock_dialog:
                mock_dialog_instance = MagicMock()
                mock_dialog_instance.ShowModal.return_value = wx.ID_OK
                mock_dialog_instance.GetPath.return_value = str(temp_path)
                mock_dialog_instance.__enter__.return_value = mock_dialog_instance
                mock_dialog_instance.__exit__.return_value = None
                mock_dialog.return_value = mock_dialog_instance

                # Mock authenticator
                with patch.object(
                    controller.authenticator, "authenticate"
                ) as mock_auth:
                    from simple_otp.core.accounts_manager import AccountsManager

                    mock_manager = AccountsManager(
                        storage_path=temp_path, auto_create=False
                    )
                    mock_auth.return_value = (mock_manager, "test_password")

                    file_path, manager, password = controller.open_file()

                    assert file_path == temp_path
                    assert manager is not None
                    assert password == "test_password"
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_open_file_with_path_success(self, app, controller):
        """Test opening file with provided path."""
        # Create a temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write('{"accounts": []}')

        try:
            # Mock authenticator
            with patch.object(controller.authenticator, "authenticate") as mock_auth:
                from simple_otp.core.accounts_manager import AccountsManager

                mock_manager = AccountsManager(
                    storage_path=temp_path, auto_create=False
                )
                mock_auth.return_value = (mock_manager, "test_password")

                file_path, manager, password = controller.open_file(temp_path)

                assert file_path == temp_path
                assert manager is not None
                assert password == "test_password"
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_open_file_cancelled_dialog(self, app, controller):
        """Test opening file cancelled at dialog."""
        # Mock file dialog to return CANCEL
        with patch("simple_otp.ui.file_controller.wx.FileDialog") as mock_dialog:
            mock_dialog_instance = MagicMock()
            mock_dialog_instance.ShowModal.return_value = wx.ID_CANCEL
            mock_dialog_instance.__enter__.return_value = mock_dialog_instance
            mock_dialog_instance.__exit__.return_value = None
            mock_dialog.return_value = mock_dialog_instance

            file_path, manager, password = controller.open_file()

            assert file_path is None
            assert manager is None
            assert password is None

    def test_open_file_not_found(self, app, controller):
        """Test opening non-existent file."""
        non_existent_path = Path("non_existent_file.json")

        # Mock MessageBox to avoid showing warning
        with patch("simple_otp.ui.file_controller.wx.MessageBox"):
            file_path, manager, password = controller.open_file(non_existent_path)

            assert file_path is None
            assert manager is None
            assert password is None

    def test_open_file_authentication_failed(self, app, controller):
        """Test opening file when authentication fails."""
        # Create a temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write('{"accounts": []}')

        try:
            # Mock authenticator to return None (authentication failed)
            with patch.object(controller.authenticator, "authenticate") as mock_auth:
                mock_auth.return_value = (None, None)

                file_path, manager, password = controller.open_file(temp_path)

                assert file_path is None
                assert manager is None
                assert password is None
        finally:
            if temp_path.exists():
                temp_path.unlink()
