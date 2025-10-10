"""Tests for RecentFilesManager."""

import tempfile
from pathlib import Path

import pytest

from simple_otp.constants import MAX_RECENT_FILES
from simple_otp.core.recent_files_manager import RecentFilesManager
from simple_otp.core.settings_manager import SettingsManager


class TestRecentFilesManager:
    """Tests for RecentFilesManager."""

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

    def test_add_file(self, temp_settings):
        """Test adding a file to recent files."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        file_path = Path("test_file.json")
        manager.add_file(file_path)

        recent_files = manager.get_recent_files()
        assert len(recent_files) == 1
        assert recent_files[0] == file_path.resolve()

    def test_add_multiple_files(self, temp_settings):
        """Test adding multiple files to recent files."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        file1 = Path("file1.json")
        file2 = Path("file2.json")
        file3 = Path("file3.json")

        manager.add_file(file1)
        manager.add_file(file2)
        manager.add_file(file3)

        recent_files = manager.get_recent_files()
        assert len(recent_files) == 3
        # Most recent should be first
        assert recent_files[0] == file3.resolve()
        assert recent_files[1] == file2.resolve()
        assert recent_files[2] == file1.resolve()

    def test_add_duplicate_file_moves_to_front(self, temp_settings):
        """Test that adding a duplicate file moves it to the front."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        file1 = Path("file1.json")
        file2 = Path("file2.json")

        manager.add_file(file1)
        manager.add_file(file2)
        manager.add_file(file1)  # Add file1 again

        recent_files = manager.get_recent_files()
        assert len(recent_files) == 2  # No duplicates
        assert recent_files[0] == file1.resolve()  # file1 is now first
        assert recent_files[1] == file2.resolve()

    def test_max_recent_files_limit(self, temp_settings):
        """Test that recent files list is limited to MAX_RECENT_FILES."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        # Add more than MAX_RECENT_FILES files
        for i in range(MAX_RECENT_FILES + 5):
            manager.add_file(Path(f"file{i}.json"))

        recent_files = manager.get_recent_files()
        assert len(recent_files) == MAX_RECENT_FILES

    def test_remove_file(self, temp_settings):
        """Test removing a file from recent files."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        file1 = Path("file1.json")
        file2 = Path("file2.json")

        manager.add_file(file1)
        manager.add_file(file2)

        # Remove file1
        result = manager.remove_file(file1)
        assert result is True

        recent_files = manager.get_recent_files()
        assert len(recent_files) == 1
        assert recent_files[0] == file2.resolve()

    def test_remove_nonexistent_file(self, temp_settings):
        """Test removing a file that doesn't exist in recent files."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        file1 = Path("file1.json")
        file2 = Path("file2.json")

        manager.add_file(file1)

        # Try to remove file2 that wasn't added
        result = manager.remove_file(file2)
        assert result is False

        recent_files = manager.get_recent_files()
        assert len(recent_files) == 1
        assert recent_files[0] == file1.resolve()

    def test_clear_history(self, temp_settings):
        """Test clearing recent files history."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        # Add some files
        manager.add_file(Path("file1.json"))
        manager.add_file(Path("file2.json"))
        manager.add_file(Path("file3.json"))

        # Clear history
        manager.clear_history()

        recent_files = manager.get_recent_files()
        assert len(recent_files) == 0

    def test_has_recent_files(self, temp_settings):
        """Test checking if there are recent files."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        # Initially empty
        assert manager.has_recent_files() is False

        # Add a file
        manager.add_file(Path("file1.json"))
        assert manager.has_recent_files() is True

        # Clear history
        manager.clear_history()
        assert manager.has_recent_files() is False

    def test_get_recent_files_strings(self, temp_settings):
        """Test getting recent files as strings."""
        settings_manager, _ = temp_settings
        manager = RecentFilesManager(settings_manager)

        file1 = Path("file1.json")
        manager.add_file(file1)

        recent_strings = manager.get_recent_files_strings()
        assert len(recent_strings) == 1
        assert recent_strings[0] == str(file1.resolve())
