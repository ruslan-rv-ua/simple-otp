# Main Window Implementation

## Overview
The main window has been implemented with the following features:

## Window Layout
- **Maximized window** - Opens in maximized state by default
- **Vertical layout** with two main components:
  1. Search editor (top)
  2. Accounts list (bottom - fills remaining space)

## Search Functionality
- Search text control at the top of the window
- **Minimum 3 characters** required to activate filtering
- **Multi-word filtering**: All words must be present in either account name or issuer
- Uses ObjectListView3's built-in `Filter.Predicate()` for efficient filtering
- Filter is cleared when search text is less than 3 characters

## Accounts List
- Implemented using **ObjectListView3** (enhanced wx.ListCtrl)
- **Single column**: "Name" - displays formatted as "issuer - name" (or just "name" if no issuer)
- **Single selection mode** (wx.LC_SINGLE_SEL)
- Currently populated with sample accounts for testing
- **Item activation** (double-click or Enter) opens TOTP dialog

## TOTP Dialog
The TOTP dialog (`totp_dialog.py`) is shown when a list item is activated:

### Features
- **Current Password**: Displays the currently valid OTP code
- **Next Password**: Displays the next OTP code (for the next time interval)
- **Copy Buttons**: Copy password to clipboard without spaces (using pyperclip)
- **Progress Bar**: Visual countdown showing time remaining in current interval
  - Progress bar fills from 100% to 0% as the interval time elapses
- **Auto-refresh**: Updates every 100ms using wx.Timer for smooth progress
- **Audio Alert**: Plays sound when less than 5 seconds remain (once per interval)

### Password Formatting
- OTP codes are displayed with **digits grouped by 2** (e.g., "12 34 56" or "12 34 56 78")
- Spaces are shown for readability but removed when copying to clipboard

### Technical Details
- Uses `pyotp.TOTP.now()` for current code
- Uses `pyotp.TOTP.at(time)` for next code
- Timer updates display and progress bar every 100ms
- Dialog is centered on parent window
- Proper cleanup of timer on dialog close
- Audio player plays `under_5_seconds.wav` asynchronously

## Audio Player
The audio player (`audio_player.py`) provides sound playback for UI events:

### Features
- **Asynchronous playback**: All sounds play in background (non-blocking)
- **File-based**: WAV files played directly from disk
- **Auto-discovery**: Scans audio directory on initialization
- **Error handling**: Raises clear exceptions with helpful messages

### Usage

#### Option 1: Use global instance (recommended)
```python
from simple_otp.ui.audio_player import audio_player

# Use global instance directly (already initialized)
if audio_player:
    audio_player.play("sound.wav")
    
    # Get available files
    files = audio_player.get_available_files()
    
    # Stop all sounds
    audio_player.stop()
```

#### Option 2: Create custom instance
```python
from pathlib import Path
from simple_otp.ui.audio_player import AudioPlayer

# Initialize custom instance
sounds_dir = Path(__file__).parent / "assets" / "sounds"
player = AudioPlayer(sounds_dir)

# Play sound (always async)
player.play("sound.wav")
```

### Technical Details
- Uses `winsound.PlaySound()` with `SND_FILENAME | SND_ASYNC`
- No memory caching - lightweight and efficient
- Validates directory on initialization
- See `docs/AUDIO_PLAYER_ASYNC_FIX.md` for implementation details

## Menu Bar

### Account Menu
- **Add** (F7) - Opens Add Account dialog to create new TOTP accounts
- **Delete** (Del) - Deletes the selected account with confirmation

### Help Menu
- **About** - Shows proper About dialog with:
  - App name: "Simple OTP"
  - Version from pyproject.toml (dynamically loaded)
  - Description
  - Developer info

## Technical Details

### Key Components
- `simple_otp/ui/main_window.py` - Main window implementation
- `simple_otp/ui/__init__.py` - UI package initialization
- `simple_otp/__main__.py` - Entry point that launches the GUI

### Dependencies
- **wxPython** - Native GUI framework
- **ObjectListView3** - Enhanced list control with filtering/sorting

### Running the Application
```cmd
uv run python -m simple_otp
```

## Sample Data
The application currently loads 5 sample accounts:
1. Example Service - user@example.com
2. Google - john.doe@gmail.com
3. GitHub - jane.smith@github.com
4. Company Portal - admin@company.com
5. Microsoft - test@microsoft.com

## Add Account Feature

The Add Account feature (`add_account_dialog.py`) allows users to manually add new TOTP accounts:

### Features
- **Required Fields**: Name and Secret (Base32)
- **Optional Fields**: Issuer, Digits (6/8), Digest Algorithm (SHA1/256/512), Interval
- **Validation**: 
  - Name and Secret are required
  - Secret must be valid Base32 format
  - Automatic normalization (removes spaces, converts to uppercase)
  - Prevents duplicate accounts (same name + issuer)
- **Encryption**: Secrets are encrypted with master password before storage
- **Error Handling**: Clear error messages for validation failures

See [docs/ADD_ACCOUNT_USAGE.md](../../docs/ADD_ACCOUNT_USAGE.md) for detailed usage instructions.
