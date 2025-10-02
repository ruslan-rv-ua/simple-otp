import threading
import winsound
from pathlib import Path


class AudioPlayer:
    """
    Audio player for WAV files with asynchronous playback from memory cache.

    All WAV files are loaded into memory on initialization for fast playback.
    Sounds are played asynchronously (non-blocking) using background threads.

    Raises:
        FileNotFoundError: If the audio directory does not exist
        NotADirectoryError: If audio_dir is not a directory
        OSError: If there are problems reading WAV files
    """

    def __init__(self, audio_dir: Path):
        """
        Initialize player and load all WAV files into memory.

        Args:
            audio_dir: Path to directory containing WAV files

        Raises:
            FileNotFoundError: If the audio directory does not exist
            NotADirectoryError: If audio_dir is not a directory
            OSError: If there are problems reading WAV files
        """
        self.audio_dir = Path(audio_dir)
        self.cache: dict[str, bytes] = {}
        self._load_all_wav_files()

    def _load_all_wav_files(self) -> None:
        """
        Load all WAV files from directory into memory cache.

        Raises:
            FileNotFoundError: If the audio directory does not exist
            NotADirectoryError: If audio_dir is not a directory
            OSError: If there are problems reading WAV files
        """
        if not self.audio_dir.exists():
            raise FileNotFoundError(f"Audio directory does not exist: {self.audio_dir}")

        if not self.audio_dir.is_dir():
            raise NotADirectoryError(
                f"Audio directory path is not a directory: {self.audio_dir}"
            )

        # Load all .wav files into memory
        self.cache.clear()
        for wav_file in self.audio_dir.glob("*.wav"):
            with open(wav_file, "rb") as f:
                self.cache[wav_file.name] = f.read()

    def _play_sync(self, audio_data: bytes) -> None:
        """
        Play audio data synchronously from memory (internal use).

        Args:
            audio_data: WAV file data in bytes
        """
        try:
            winsound.PlaySound(audio_data, winsound.SND_MEMORY | winsound.SND_NODEFAULT)
        except RuntimeError:
            # Silently ignore playback errors in background thread
            pass

    def play(self, filename: str) -> None:
        """
        Play WAV file asynchronously from memory cache (non-blocking).

        The sound plays in a background thread without blocking program execution.
        Audio data is played from memory for fast, responsive playback.

        Args:
            filename: Name of the WAV file (e.g., 'audio.wav')

        Raises:
            FileNotFoundError: If the requested filename is not in cache
        """
        if filename not in self.cache:
            raise FileNotFoundError(
                f"Audio file '{filename}' not found in cache. "
                f"Available files: {list(self.cache.keys())}"
            )

        # Play sound in background thread (async from caller's perspective)
        audio_data = self.cache[filename]
        thread = threading.Thread(
            target=self._play_sync, args=(audio_data,), daemon=True
        )
        thread.start()

    def stop(self) -> None:
        """Stop all currently playing sounds"""
        winsound.PlaySound(None, winsound.SND_PURGE)

    def get_available_files(self) -> list[str]:
        """
        Get list of all loaded audio filenames.

        Returns:
            List of filenames in cache
        """
        return list(self.cache.keys())

    def get_cache_size(self) -> int:
        """
        Get total size of cached audio data.

        Returns:
            Total size in bytes
        """
        return sum(len(data) for data in self.cache.values())

    def reload(self) -> None:
        """
        Clear cache and reload all WAV files from directory.

        Raises:
            FileNotFoundError: If the audio directory does not exist
            NotADirectoryError: If audio_dir is not a directory
            OSError: If there are problems reading WAV files
        """
        self._load_all_wav_files()
