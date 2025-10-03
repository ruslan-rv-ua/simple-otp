"""Unit tests for SettingsManager."""

import json
import tempfile
from pathlib import Path

import pytest

from simple_otp.core.settings_manager import SettingsManager


class TestSettingsManager:
    """Test cases for the SettingsManager class."""

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

    def test_init_creates_default_settings(self, temp_settings_file):
        """Test that initialization creates default settings file."""
        _ = SettingsManager(temp_settings_file)
        assert temp_settings_file.exists()

        # Verify default settings are written
        with open(temp_settings_file, encoding="utf-8") as f:
            data = json.load(f)
            assert "version" in data
            assert "totp" in data
            assert "audio" in data

    def test_get_existing_setting(self, settings_manager):
        """Test getting an existing setting."""
        value = settings_manager.get("totp.default_digits")
        assert value == 6

    def test_get_nested_setting(self, settings_manager):
        """Test getting a nested setting."""
        value = settings_manager.get("audio.play_password_copied_sound")
        assert value is True

    def test_get_nonexistent_setting_returns_default(self, settings_manager):
        """Test getting a non-existent setting returns default value."""
        value = settings_manager.get("nonexistent.setting", "default_value")
        assert value == "default_value"

    def test_set_existing_setting(self, settings_manager):
        """Test setting an existing setting."""
        settings_manager.set("totp.default_digits", 8)
        assert settings_manager.get("totp.default_digits") == 8

    def test_set_nested_setting(self, settings_manager):
        """Test setting a nested setting."""
        settings_manager.set("audio.warning_sound_seconds", 10)
        assert settings_manager.get("audio.warning_sound_seconds") == 10

    def test_set_new_setting(self, settings_manager):
        """Test setting a new setting that doesn't exist."""
        settings_manager.set("new.setting", "value")
        assert settings_manager.get("new.setting") == "value"

    def test_save_and_load(self, settings_manager, temp_settings_file):
        """Test saving and loading settings."""
        # Modify settings
        settings_manager.set("totp.default_digits", 8)
        settings_manager.set("audio.play_warning_sound", False)

        # Save to file
        settings_manager.save()

        # Create new manager and load from file
        new_manager = SettingsManager(temp_settings_file)

        # Verify settings were persisted
        assert new_manager.get("totp.default_digits") == 8
        assert new_manager.get("audio.play_warning_sound") is False

    def test_get_all(self, settings_manager):
        """Test getting all settings."""
        all_settings = settings_manager.get_all()

        assert isinstance(all_settings, dict)
        assert "version" in all_settings
        assert "totp" in all_settings
        assert "audio" in all_settings

    def test_reset_to_defaults(self, settings_manager):
        """Test resetting settings to defaults."""
        # Modify settings
        settings_manager.set("totp.default_digits", 8)
        settings_manager.set("audio.play_warning_sound", False)

        # Reset to defaults
        settings_manager.reset_to_defaults()

        # Verify defaults are restored
        assert settings_manager.get("totp.default_digits") == 6
        assert settings_manager.get("audio.play_warning_sound") is True

    def test_load_corrupted_file_uses_defaults(self, temp_settings_file):
        """Test that corrupted settings file falls back to defaults."""
        # Write invalid JSON
        with open(temp_settings_file, "w", encoding="utf-8") as f:
            f.write("invalid json {[")

        # Create manager - should use defaults
        manager = SettingsManager(temp_settings_file)

        # Verify defaults are used
        assert manager.get("totp.default_digits") == 6
        assert manager.get("audio.play_password_copied_sound") is True

    def test_merge_settings_with_missing_keys(self, temp_settings_file):
        """Test that loading settings with missing keys merges with defaults."""
        # Write partial settings
        partial_settings = {"totp": {"default_digits": 8}}
        with open(temp_settings_file, "w", encoding="utf-8") as f:
            json.dump(partial_settings, f)

        # Create manager - should merge with defaults
        manager = SettingsManager(temp_settings_file)

        # Verify loaded setting
        assert manager.get("totp.default_digits") == 8

        # Verify missing settings use defaults
        assert manager.get("audio.play_password_copied_sound") is True
        assert manager.get("totp.default_interval") == 30

    def test_default_settings_structure(self):
        """Test that default settings have expected structure."""
        defaults = SettingsManager.DEFAULT_SETTINGS

        # Check version
        assert "version" in defaults

        # Check TOTP settings
        assert "totp" in defaults
        assert "default_digits" in defaults["totp"]
        assert "default_interval" in defaults["totp"]
        assert "default_digest" in defaults["totp"]

        # Check behavior settings
        assert "behavior" in defaults
        assert "auto_copy_on_update" in defaults["behavior"]

        # Check audio settings
        assert "audio" in defaults
        assert "play_password_copied_sound" in defaults["audio"]
        assert "play_warning_sound" in defaults["audio"]
        assert "warning_sound_seconds" in defaults["audio"]

    def test_settings_file_encoding(self, settings_manager, temp_settings_file):
        """Test that settings file uses UTF-8 encoding."""
        # Set a value with Unicode characters
        settings_manager.set("test.unicode", "Тест UTF-8 測試")
        settings_manager.save()

        # Read file and verify encoding
        with open(temp_settings_file, encoding="utf-8") as f:
            data = json.load(f)
            assert data["test"]["unicode"] == "Тест UTF-8 測試"

    def test_concurrent_managers_same_file(self, temp_settings_file):
        """Test behavior with multiple manager instances on same file."""
        manager1 = SettingsManager(temp_settings_file)
        manager2 = SettingsManager(temp_settings_file)

        # Modify in first manager
        manager1.set("totp.default_digits", 7)
        manager1.save()

        # Load in second manager
        manager2.load()

        # Verify second manager sees changes
        assert manager2.get("totp.default_digits") == 7

    def test_audio_settings_defaults(self, settings_manager):
        """Test audio settings default values."""
        assert settings_manager.get("audio.play_password_copied_sound") is True
        assert settings_manager.get("audio.play_warning_sound") is True
        assert settings_manager.get("audio.warning_sound_seconds") == 5

    def test_behavior_settings_defaults(self, settings_manager):
        """Test behavior settings default values."""
        assert settings_manager.get("behavior.auto_copy_on_update") is False

    def test_modify_audio_settings(self, settings_manager):
        """Test modifying audio settings."""
        settings_manager.set("audio.play_password_copied_sound", False)
        settings_manager.set("audio.play_warning_sound", False)
        settings_manager.set("audio.warning_sound_seconds", 10)

        assert settings_manager.get("audio.play_password_copied_sound") is False
        assert settings_manager.get("audio.play_warning_sound") is False
        assert settings_manager.get("audio.warning_sound_seconds") == 10

    def test_modify_behavior_settings(self, settings_manager):
        """Test modifying behavior settings."""
        settings_manager.set("behavior.auto_copy_on_update", True)
        assert settings_manager.get("behavior.auto_copy_on_update") is True

    def test_audio_settings_persistence(self, settings_manager, temp_settings_file):
        """Test that audio settings persist across save/load."""
        settings_manager.set("audio.play_password_copied_sound", False)
        settings_manager.set("audio.warning_sound_seconds", 3)
        settings_manager.save()

        new_manager = SettingsManager(temp_settings_file)
        assert new_manager.get("audio.play_password_copied_sound") is False
        assert new_manager.get("audio.warning_sound_seconds") == 3

    def test_locale_default_is_none(self, settings_manager):
        """Test that locale defaults to None (auto-detect)."""
        assert settings_manager.get("locale") is None

    def test_set_locale(self, settings_manager):
        """Test setting and getting locale."""
        settings_manager.set("locale", "uk-UA")
        assert settings_manager.get("locale") == "uk-UA"

        settings_manager.set("locale", "en-US")
        assert settings_manager.get("locale") == "en-US"

    def test_locale_persistence(self, settings_manager, temp_settings_file):
        """Test that locale setting persists across save/load."""
        settings_manager.set("locale", "uk-UA")
        settings_manager.save()

        new_manager = SettingsManager(temp_settings_file)
        assert new_manager.get("locale") == "uk-UA"
