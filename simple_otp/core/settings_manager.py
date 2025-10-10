"""Settings manager for simple-otp application."""

import copy
import json
from pathlib import Path
from typing import Any

from simple_otp.core.logger import logger


class SettingsManager:
    """Manages application settings with JSON persistence."""

    # Default settings structure
    DEFAULT_SETTINGS = {
        "version": "1.0",
        "locale": None,  # None = auto-detect, or explicit locale like "en-US", "uk-UA"
        "totp": {
            "default_digits": 6,
            "default_interval": 30,
            "default_digest": "SHA1",
        },
        "behavior": {
            "auto_copy_on_update": False,
            "hide_passwords": True,
            "auto_speak_password": False,
        },
        "audio": {
            "play_current_copied_sound": True,
            "play_next_copied_sound": True,
            "play_password_updated_sound": True,
            "play_warning_sound": True,
            "warning_sound_seconds": 5,
        },
        "files": {
            "recent_files": [],
            "open_last_file_on_startup": True,
        },
    }

    def __init__(self, settings_file: Path | None = None):
        """
        Initialize the settings manager.

        Args:
            settings_file: Path to settings file. If None, uses default location
                          (settings.json next to __main__.py)
        """
        if settings_file is None:
            # Get the directory containing __main__.py
            app_dir = Path(__file__).parent.parent
            self.settings_file = app_dir / "settings.json"
        else:
            self.settings_file = Path(settings_file)

        logger.debug(f"SettingsManager initialized with file: {self.settings_file}")

        self._settings: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """
        Load settings from JSON file.

        Creates default settings if file doesn't exist.
        """
        if self.settings_file.exists():
            try:
                with open(self.settings_file, encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                    # Merge loaded settings with defaults to handle missing keys
                    self._settings = self._merge_settings(
                        copy.deepcopy(self.DEFAULT_SETTINGS), loaded_settings
                    )
                logger.info(f"Settings loaded from {self.settings_file}")
            except json.JSONDecodeError as e:
                logger.error(
                    f"Settings file corrupted (JSON error): {e}, using defaults"
                )
                # If file is corrupted or unreadable, use defaults
                self._settings = copy.deepcopy(self.DEFAULT_SETTINGS)
                # Try to save defaults
                try:
                    self.save()
                except OSError:
                    pass  # Ignore save errors during load
            except OSError as e:
                logger.error(f"Failed to load settings file: {e}, using defaults")
                self._settings = copy.deepcopy(self.DEFAULT_SETTINGS)
        else:
            logger.info("Settings file not found, using defaults and creating file")
            # First run - use defaults and create the file
            self._settings = copy.deepcopy(self.DEFAULT_SETTINGS)
            try:
                self.save()
            except OSError:
                pass  # Ignore save errors during initial load

    def save(self) -> None:
        """Save current settings to JSON file."""
        # Ensure parent directory exists
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self._settings, f, indent=2, ensure_ascii=False)

        logger.debug(f"Settings saved to {self.settings_file}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value by dot-separated key path.

        Args:
            key: Dot-separated key path (e.g., "ui.theme" or "security.auto_copy")
            default: Default value if key not found

        Returns:
            Setting value or default if not found
        """
        keys = key.split(".")
        value = self._settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value by dot-separated key path.

        Args:
            key: Dot-separated key path (e.g., "ui.theme")
            value: Value to set
        """
        keys = key.split(".")
        target = self._settings

        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]

        # Set the value
        target[keys[-1]] = value

    def get_all(self) -> dict[str, Any]:
        """
        Get all settings as a dictionary.

        Returns:
            Copy of all settings
        """
        return self._settings.copy()

    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        logger.info("Resetting all settings to default values")
        self._settings = copy.deepcopy(self.DEFAULT_SETTINGS)

    def _merge_settings(
        self, defaults: dict[str, Any], loaded: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Recursively merge loaded settings with defaults.

        Args:
            defaults: Default settings dictionary
            loaded: Loaded settings dictionary

        Returns:
            Merged settings dictionary
        """
        result = defaults.copy()

        for key, value in loaded.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                # Recursively merge nested dictionaries
                result[key] = self._merge_settings(result[key], value)
            else:
                # Override with loaded value
                result[key] = value

        return result
