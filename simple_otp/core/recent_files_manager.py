"""Manager for recent files list."""

from pathlib import Path

from simple_otp.constants import MAX_RECENT_FILES
from simple_otp.core.logger import logger
from simple_otp.core.settings_manager import SettingsManager


class RecentFilesManager:
    """Manages recent files list in settings."""

    def __init__(self, settings_manager: SettingsManager):
        """
        Initialize the recent files manager.

        Args:
            settings_manager: Settings manager instance for persistence
        """
        self.settings = settings_manager

    def add_file(self, file_path: Path) -> None:
        """
        Add file to recent files list.

        If the file already exists in the list, it will be moved to the front.
        The list is limited to MAX_RECENT_FILES entries.

        Args:
            file_path: Path to the file to add
        """
        # Get current recent files list
        recent_files = self.get_recent_files_strings()

        # Convert to string for comparison
        file_str = str(file_path.resolve())

        # Remove if already exists (to move to front)
        if file_str in recent_files:
            recent_files.remove(file_str)
            logger.debug(f"Moved existing file to front of recent list: {file_str}")
        else:
            logger.info(f"Added new file to recent list: {file_str}")

        # Add to front
        recent_files.insert(0, file_str)

        # Keep only MAX_RECENT_FILES entries
        recent_files = recent_files[:MAX_RECENT_FILES]

        # Save to settings
        self.settings.set("files.recent_files", recent_files)
        self.settings.save()

    def remove_file(self, file_path: Path) -> bool:
        """
        Remove file from recent files list.

        Args:
            file_path: Path to the file to remove

        Returns:
            True if file was removed, False if it wasn't in the list
        """
        # Get current recent files list
        recent_files = self.get_recent_files_strings()

        # Convert to string for comparison
        file_str = str(file_path.resolve())

        if file_str in recent_files:
            recent_files.remove(file_str)
            self.settings.set("files.recent_files", recent_files)
            self.settings.save()
            logger.info(f"Removed file from recent list: {file_str}")
            return True

        logger.debug(
            f"Attempted to remove non-existent file from recent list: {file_str}"
        )
        return False

    def get_recent_files(self) -> list[Path]:
        """
        Get list of recent files as Path objects.

        Returns:
            List of Path objects for recent files
        """
        recent_files_strings = self.get_recent_files_strings()
        return [Path(file_str) for file_str in recent_files_strings]

    def get_recent_files_strings(self) -> list[str]:
        """
        Get list of recent files as strings.

        Returns:
            List of file paths as strings
        """
        return self.settings.get("files.recent_files", [])

    def clear_history(self) -> None:
        """Clear all recent files from history."""
        count = len(self.get_recent_files_strings())
        self.settings.set("files.recent_files", [])
        self.settings.save()
        logger.info(f"Cleared recent files history ({count} items)")

    def has_recent_files(self) -> bool:
        """
        Check if there are any recent files.

        Returns:
            True if there are recent files, False otherwise
        """
        return len(self.get_recent_files_strings()) > 0
