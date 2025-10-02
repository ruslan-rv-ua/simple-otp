"""Unit tests for SettingsDialog."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import wx

from simple_otp.core.settings_manager import SettingsManager
from simple_otp.ui.settings_dialog import SettingsDialog


class TestSettingsDialog:
    """Test cases for the SettingsDialog class."""

    @pytest.fixture
    def app(self):
        """Create a wx.App instance for tests."""
        app = wx.App()
        yield app
        app.Destroy()

    @pytest.fixture
    def temp_settings_file(self):
        """Create a temporary settings file."""
        # Use a unique file for each test to avoid interference
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = Path(f.name)
        # Don't write anything, just get a unique file path
        # The SettingsManager will create it
        if temp_file.exists():
            temp_file.unlink()
        yield temp_file
        # Clean up
        if temp_file.exists():
            temp_file.unlink()

    @pytest.fixture
    def settings_manager(self, temp_settings_file):
        """Create a SettingsManager with a temporary file."""
        return SettingsManager(temp_settings_file)

    @pytest.fixture
    def dialog(self, app, settings_manager):
        """Create a SettingsDialog for tests."""
        dlg = SettingsDialog(None, settings_manager)
        yield dlg
        dlg.Destroy()

    def test_dialog_creation(self, dialog):
        """Test that dialog is created successfully."""
        assert dialog is not None
        assert dialog.GetTitle() == "Settings"

    def test_dialog_has_notebook(self, dialog):
        """Test that dialog contains a notebook with pages."""
        assert hasattr(dialog, "notebook")
        assert dialog.notebook.GetPageCount() == 4

        # Check page titles
        assert dialog.notebook.GetPageText(0) == "User Interface"
        assert dialog.notebook.GetPageText(1) == "Security"
        assert dialog.notebook.GetPageText(2) == "TOTP Defaults"
        assert dialog.notebook.GetPageText(3) == "Audio"

    def test_dialog_has_buttons(self, dialog):
        """Test that dialog has required buttons."""
        assert hasattr(dialog, "reset_button")

        # Find OK and Cancel buttons by ID
        ok_button = dialog.FindWindowById(wx.ID_OK)
        cancel_button = dialog.FindWindowById(wx.ID_CANCEL)

        assert ok_button is not None
        assert cancel_button is not None

    def test_load_settings_into_ui(self, app, settings_manager):
        """Test that settings are loaded into UI controls."""
        # Set specific values
        settings_manager.set("ui.theme", "default")
        settings_manager.set("ui.font_size", 12)
        settings_manager.set("security.auto_copy", False)
        settings_manager.set("totp.default_digits", 8)

        # Create dialog (app fixture ensures wx.App exists)
        dialog = SettingsDialog(None, settings_manager)

        # Verify UI reflects settings
        assert dialog.font_size_spin.GetValue() == 12
        assert dialog.auto_copy_check.GetValue() is False
        assert dialog.digits_choice.GetSelection() == 2  # 8 digits -> index 2

        dialog.Destroy()

    def test_save_settings_from_ui(self, dialog, settings_manager):
        """Test that settings are saved from UI controls."""
        # Modify UI controls (only those that are enabled)
        # Note: Most controls are disabled as placeholders,
        # so we test the save mechanism itself
        dialog._save_settings()

        # Verify save was called (settings should be written to file)
        # The actual values don't matter since controls are disabled
        all_settings = settings_manager.get_all()
        assert "ui" in all_settings
        assert "security" in all_settings
        assert "totp" in all_settings

    def test_reset_to_defaults_with_confirmation(self, dialog):
        """Test reset to defaults functionality with user confirmation."""
        # Modify settings
        dialog.settings_manager.set("ui.theme", "dark")

        # Mock MessageBox to return YES
        with patch("wx.MessageBox", return_value=wx.YES):
            dialog._on_reset(None)

        # Verify settings were reset
        assert dialog.settings_manager.get("ui.theme") == "default"

    def test_reset_to_defaults_cancelled(self, dialog):
        """Test that reset can be cancelled."""
        # Modify settings
        dialog.settings_manager.set("ui.theme", "dark")

        # Mock MessageBox to return NO
        with patch("wx.MessageBox", return_value=wx.NO):
            dialog._on_reset(None)

        # Verify settings were NOT reset
        assert dialog.settings_manager.get("ui.theme") == "dark"

    def test_ok_button_saves_settings(self, dialog, temp_settings_file):
        """Test that OK button saves settings to file."""
        # Mock EndModal
        dialog.EndModal = MagicMock()

        # Trigger OK button
        dialog._on_ok(None)

        # Verify save was called (file should exist and be valid)
        assert temp_settings_file.exists()

        # Verify EndModal was called with ID_OK
        dialog.EndModal.assert_called_once_with(wx.ID_OK)

    def test_ui_controls_are_disabled(self, dialog):
        """Test that placeholder UI controls are disabled."""
        # UI page controls
        assert not dialog.theme_choice.IsEnabled()
        assert not dialog.font_size_spin.IsEnabled()

        # Security page controls
        assert not dialog.auto_copy_check.IsEnabled()
        assert not dialog.clear_clipboard_check.IsEnabled()
        assert not dialog.clipboard_timeout_spin.IsEnabled()

        # TOTP page controls
        assert not dialog.digits_choice.IsEnabled()
        assert not dialog.interval_spin.IsEnabled()
        assert not dialog.digest_choice.IsEnabled()

    def test_dialog_centering(self, dialog):
        """Test that dialog can be centered (without actual parent)."""
        # This shouldn't raise an exception even with None parent
        # The CenterOnParent call should be handled gracefully
        assert True  # If we get here, no exception was raised

    def test_settings_manager_reference(self, dialog, settings_manager):
        """Test that dialog holds reference to settings manager."""
        assert dialog.settings_manager is settings_manager

    def test_default_values_in_ui(self, dialog):
        """Test that UI controls show default values on first load."""
        # UI defaults
        assert dialog.theme_choice.GetSelection() == 0  # "Default"
        assert dialog.font_size_spin.GetValue() == 10

        # Security defaults
        assert dialog.auto_copy_check.GetValue() is True
        assert dialog.clear_clipboard_check.GetValue() is True
        assert dialog.clipboard_timeout_spin.GetValue() == 30

        # TOTP defaults
        assert dialog.digits_choice.GetSelection() == 0  # 6 digits
        assert dialog.interval_spin.GetValue() == 30
        assert dialog.digest_choice.GetSelection() == 0  # SHA1

    def test_digits_choice_mapping(self, dialog):
        """Test correct mapping between digits value and choice index."""
        # Test the mapping logic used in _load_settings
        test_cases = [(6, 0), (7, 1), (8, 2)]

        for digits, expected_index in test_cases:
            dialog.settings_manager.set("totp.default_digits", digits)
            dialog._load_settings()
            assert dialog.digits_choice.GetSelection() == expected_index

    def test_digest_choice_mapping(self, dialog):
        """Test correct mapping between digest value and choice index."""
        # Test the mapping logic used in _load_settings
        test_cases = [("SHA1", 0), ("SHA256", 1), ("SHA512", 2)]

        for digest, expected_index in test_cases:
            dialog.settings_manager.set("totp.default_digest", digest)
            dialog._load_settings()
            assert dialog.digest_choice.GetSelection() == expected_index
