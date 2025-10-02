"""Tests for AudioPlayer class."""

import tempfile
from pathlib import Path

import pytest

from simple_otp.ui.audio_player import AudioPlayer


class TestAudioPlayer:
    """Test cases for AudioPlayer."""

    def test_init_with_nonexistent_directory_raises_error(self):
        """
        Test initializing with non-existent directory raises error.
        """
        non_existent_dir = Path("/this/does/not/exist")
        with pytest.raises(FileNotFoundError, match="Audio directory does not exist"):
            AudioPlayer(non_existent_dir)

    def test_init_with_file_instead_of_directory_raises_error(self):
        """
        Test initializing with file raises NotADirectoryError.
        """
        # Create a temporary file and close it before testing
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_path = Path(tmp_file.name)
        tmp_file.close()  # Close file handle on Windows

        try:
            with pytest.raises(NotADirectoryError, match="is not a directory"):
                AudioPlayer(tmp_path)
        finally:
            tmp_path.unlink()

    def test_init_with_empty_directory(self):
        """Test that initializing with empty directory works."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            player = AudioPlayer(Path(tmp_dir))
            assert player.cache == {}
            assert player.get_available_files() == []
            assert player.get_cache_size() == 0

    def test_play_nonexistent_file_raises_error(self):
        """Test that playing a non-existent file raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            player = AudioPlayer(Path(tmp_dir))
            with pytest.raises(FileNotFoundError, match="not found in cache"):
                player.play("nonexistent.wav")

    def test_get_available_files(self):
        """Test getting list of available files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create dummy WAV files (not real format, for testing only)
            wav1 = tmp_path / "sound1.wav"
            wav2 = tmp_path / "sound2.wav"
            txt_file = tmp_path / "not_a_wav.txt"

            wav1.write_bytes(b"FAKE_WAV_DATA_1")
            wav2.write_bytes(b"FAKE_WAV_DATA_2")
            txt_file.write_text("This should be ignored")

            player = AudioPlayer(tmp_path)

            available_files = player.get_available_files()
            assert len(available_files) == 2
            assert "sound1.wav" in available_files
            assert "sound2.wav" in available_files
            assert "not_a_wav.txt" not in available_files

    def test_get_cache_size(self):
        """Test getting total cache size."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create dummy WAV files with known sizes
            wav1 = tmp_path / "sound1.wav"
            wav2 = tmp_path / "sound2.wav"

            data1 = b"FAKE_WAV_DATA_1"
            data2 = b"FAKE_WAV_DATA_2"

            wav1.write_bytes(data1)
            wav2.write_bytes(data2)

            player = AudioPlayer(tmp_path)

            expected_size = len(data1) + len(data2)
            assert player.get_cache_size() == expected_size

    def test_reload(self):
        """Test reloading WAV files from directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create initial WAV file
            wav1 = tmp_path / "sound1.wav"
            wav1.write_bytes(b"FAKE_WAV_DATA_1")

            player = AudioPlayer(tmp_path)
            assert len(player.get_available_files()) == 1

            # Add another WAV file
            wav2 = tmp_path / "sound2.wav"
            wav2.write_bytes(b"FAKE_WAV_DATA_2")

            # Reload should pick up the new file
            player.reload()
            assert len(player.get_available_files()) == 2
            assert "sound1.wav" in player.get_available_files()
            assert "sound2.wav" in player.get_available_files()

    def test_stop(self):
        """Test stop method (should not raise exception)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            player = AudioPlayer(Path(tmp_dir))
            # Stop should work even without any sounds playing
            player.stop()
