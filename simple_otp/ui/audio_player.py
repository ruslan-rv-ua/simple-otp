import winsound
from pathlib import Path


class AudioPlayer:
    """
    Audio player that automatically caches all WAV files from a directory
    All files are loaded into memory on initialization for fast playback
    """

    def __init__(self, audio_dir: Path):
        """
        Initialize player and load all WAV files from directory

        Args:
            audio_dir: Path to directory containing WAV files
        """
        self.audio_dir = Path(audio_dir)
        self.cache: Dict[str, bytes] = {}
        self._load_all_wav_files()

    def _load_all_wav_files(self) -> None:
        """Load all WAV files from the directory into cache"""
        if not self.audio_dir.exists():
            return

        if not self.audio_dir.is_dir():
            return

        # Find and load all .wav files
        for wav_file in self.audio_dir.glob("*.wav"):
            try:
                with open(wav_file, "rb") as f:
                    self.cache[wav_file.name] = f.read()
            except Exception:
                pass  # Skip files that can't be read

    def play(self, filename: str, async_mode: bool = True) -> bool:
        """
        Play WAV file from memory cache

        Args:
            filename: Name of the WAV file (e.g., 'audio.wav')
            async_mode: If True, play asynchronously in background

        Returns:
            True if playback started successfully, False otherwise
        """
        if filename not in self.cache:
            return False

        try:
            flags = winsound.SND_MEMORY
            if async_mode:
                flags |= winsound.SND_ASYNC

            winsound.PlaySound(self.cache[filename], flags)
            return True
        except Exception:
            return False

    def stop(self) -> None:
        """Stop all currently playing sounds"""
        winsound.PlaySound(None, winsound.SND_PURGE)

    def get_loaded_files(self) -> list[str]:
        """
        Get list of all loaded filenames

        Returns:
            List of filenames in cache
        """
        return list(self.cache.keys())

    def get_cache_size(self) -> int:
        """
        Get total size of cached audio data

        Returns:
            Total size in bytes
        """
        return sum(len(data) for data in self.cache.values())

    def reload(self) -> None:
        """Clear cache and reload all WAV files from directory"""
        self.cache.clear()
        self._load_all_wav_files()
