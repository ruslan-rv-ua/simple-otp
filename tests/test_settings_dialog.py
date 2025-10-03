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
        from simple_otp.core.i18n import init_i18n

        # Ensure English locale for consistent test results
        init_i18n(locale="en-US", auto_detect=False)

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
        assert dialog.notebook.GetPageCount() == 3

        # Check page titles
        assert dialog.notebook.GetPageText(0) == "Behavior"
        assert dialog.notebook.GetPageText(1) == "Audio"
        assert dialog.notebook.GetPageText(2) == "TOTP Defaults"

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
        settings_manager.set("totp.default_digits", 8)
        settings_manager.set("totp.default_interval", 60)
        settings_manager.set("audio.play_warning_sound", False)

        # Create dialog (app fixture ensures wx.App exists)
        dialog = SettingsDialog(None, settings_manager)

        # Verify UI reflects settings
        assert dialog.digits_choice.GetSelection() == 2  # 8 digits -> index 2
        assert dialog.interval_spin.GetValue() == 60
        assert dialog.play_warning_check.GetValue() is False

        dialog.Destroy()

    def test_save_settings_from_ui(self, dialog, settings_manager):
        """Test that settings are saved from UI controls."""
        # Modify UI controls
        dialog.digits_choice.SetSelection(1)  # 7 digits
        dialog.interval_spin.SetValue(45)
        dialog.play_warning_check.SetValue(False)

        dialog._save_settings()

        # Verify settings were saved
        assert settings_manager.get("totp.default_digits") == 7
        assert settings_manager.get("totp.default_interval") == 45
        assert settings_manager.get("audio.play_warning_sound") is False

    def test_reset_to_defaults_with_confirmation(self, dialog):
        """Test reset to defaults functionality with user confirmation."""
        # Modify settings
        dialog.settings_manager.set("totp.default_digits", 8)

        # Mock MessageBox to return YES
        with patch("wx.MessageBox", return_value=wx.YES):
            dialog._on_reset(None)

        # Verify settings were reset
        assert dialog.settings_manager.get("totp.default_digits") == 6

    def test_reset_to_defaults_cancelled(self, dialog):
        """Test that reset can be cancelled."""
        # Modify settings
        dialog.settings_manager.set("totp.default_digits", 8)

        # Mock MessageBox to return NO
        with patch("wx.MessageBox", return_value=wx.NO):
            dialog._on_reset(None)

        # Verify settings were NOT reset
        assert dialog.settings_manager.get("totp.default_digits") == 8

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

    def test_ui_controls_are_enabled(self, dialog):
        """Test that all UI controls are enabled."""
        # TOTP page controls
        assert dialog.digits_choice.IsEnabled()
        assert dialog.interval_spin.IsEnabled()
        assert dialog.digest_choice.IsEnabled()

        # Audio page controls
        assert dialog.play_password_copied_check.IsEnabled()
        assert dialog.play_warning_check.IsEnabled()
        assert dialog.auto_copy_on_update_check.IsEnabled()

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
        # TOTP defaults
        assert dialog.digits_choice.GetSelection() == 0  # 6 digits
        assert dialog.interval_spin.GetValue() == 30
        assert dialog.digest_choice.GetSelection() == 0  # SHA1

        # Behavior defaults
        assert dialog.auto_copy_on_update_check.GetValue() is False

        # Audio defaults
        assert dialog.play_password_copied_check.GetValue() is True
        assert dialog.play_warning_check.GetValue() is True
        assert dialog.warning_seconds_spin.GetValue() == 5

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
