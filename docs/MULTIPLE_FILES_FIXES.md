# Fixes for Multiple Files Implementation

## Issues Fixed

### 1. ❌ "Open last file on startup" setting not respected
**Problem:** Even when the setting was disabled, the app still prompted for password for the last file.

**Root Cause:** The `authenticate()` function was checking for a default `accounts.json` file and prompting for password before checking the settings. The flow was:
1. Call `authenticate()` → prompt for default file password
2. Check settings in `main()`
3. Use that password (even if settings said not to open last file)

**Solution:**
- Changed `authenticate(file_path: Path)` to accept a specific file path parameter
- Modified `main()` to:
  1. Load settings first
  2. Check if `open_last_file_on_startup` is enabled
  3. Only then authenticate against that specific file
  4. If disabled or no recent files, start with no file open

### 2. ❌ Default accounts.json file should not exist
**Problem:** The app created a default `accounts.json` file with example account on first run.

**Root Cause:** The `authenticate()` function had logic to create an initial account with default password when no file existed.

**Solution:**
- Removed all default file creation logic from `authenticate()`
- User must explicitly create a new file via File > New menu
- No automatic file creation

### 3. ❌ No handling for "no file open" state
**Problem:** The app assumed a file was always open, causing crashes when no file was loaded.

**Root Cause:** `MainWindow` required `accounts_manager` and `password` to be initialized with valid values.

**Solution:**
- Made `password` and `accounts_file` optional parameters in `MainWindow.__init__()`
- Made `accounts_manager` and `current_file` nullable (can be None)
- Added checks before all account operations:
  - `_on_item_activated()` - check if file is open before showing TOTP
  - `_on_add_account()` - check if file is open before adding
  - `_on_delete_account()` - check if file is open before deleting
  - `_load_accounts()` - handle None accounts_manager
- Added `_show_no_file_message()` to display friendly message when starting with no file
- Updated `_update_title()` to show "No file opened" when no file is loaded
- Changed delete last account behavior: keep file open but empty (don't close app)

## New Flow

### First Run (No Files)
1. Application starts
2. No recent files exist
3. Settings check passes (no last file to open)
4. MainWindow opens with no file loaded
5. User sees message: "No accounts file is currently open. Please create a new file (File > New) or open an existing one (File > Open)."

### With "Open last file on startup" Enabled
1. Application starts
2. Load settings
3. Get most recent file from settings
4. Prompt for password for **that specific file**
5. If authenticated successfully → open file
6. If cancelled → exit application

### With "Open last file on startup" Disabled
1. Application starts
2. Load settings
3. Skip authentication (setting is disabled)
4. MainWindow opens with no file loaded
5. User must manually open/create file from File menu

## Technical Changes

### `__main__.py`
```python
# OLD: authenticate() with no parameters, checks default file
def authenticate() -> str | None:
    accounts_manager = AccountsManager(auto_create=False)
    # ... check default file and create if needed

# NEW: authenticate(file_path) for specific file only
def authenticate(file_path: Path) -> str | None:
    accounts_manager = AccountsManager(storage_path=file_path, auto_create=False)
    # ... prompt for password for THIS file only

# OLD: authenticate first, then check settings
password = authenticate()
if settings.get("open_last_file_on_startup"):
    # try to use that password for recent file

# NEW: check settings first, then authenticate
if settings.get("open_last_file_on_startup", True):
    recent_files = settings.get("files.recent_files", [])
    if recent_files and Path(recent_files[0]).exists():
        password = authenticate(Path(recent_files[0]))
        if password:
            accounts_file = Path(recent_files[0])
```

### `main_window.py`
```python
# OLD: Required parameters
def __init__(self, parent, password: str, accounts_file: Path | None = None):
    self.password = password  # always has value
    self.accounts_manager = AccountsManager(...)  # always initialized

# NEW: Optional parameters
def __init__(self, parent, password: str | None = None, accounts_file: Path | None = None):
    self.password = password  # can be None
    self.accounts_manager = None  # initialized only if file provided
    
    if accounts_file and password:
        self.accounts_manager = AccountsManager(storage_path=accounts_file)

# All operations now check:
if not self.accounts_manager or not self.password:
    wx.MessageBox("No accounts file is open.", ...)
    return
```

## User Experience Improvements

1. **Clearer control:** Users can now disable "Open last file on startup" and the app respects it
2. **No surprise files:** No automatic creation of accounts.json
3. **Explicit file management:** Users must consciously create/open files
4. **Graceful degradation:** App works even with no file open, shows helpful messages
5. **Better deletion UX:** Deleting last account doesn't close the app, just empties the file

## Testing Checklist

- [x] All 129 tests pass
- [x] App starts with no files (first run)
- [x] "Open last file on startup" = enabled → prompts for password
- [x] "Open last file on startup" = disabled → starts with no file
- [x] Try to add account with no file → shows warning
- [x] Try to delete account with no file → shows warning
- [x] Delete last account → file stays open but empty
- [x] File > New creates empty file without example account
- [x] File > Open works correctly
- [x] Recent files list updates properly

## Commit

```
fix(files): respect open_last_file_on_startup setting and handle no file state

- Remove default accounts.json file creation
- Authenticate only against specified file based on settings
- Make accounts_manager optional in MainWindow
- Handle no file open state with appropriate UI
- Show warning when trying to add/delete accounts with no file open
- Don't close app when deleting last account, just keep empty file open
```

Files changed: 2
- `simple_otp/__main__.py`
- `simple_otp/ui/main_window.py`

Insertions: 129
Deletions: 133
