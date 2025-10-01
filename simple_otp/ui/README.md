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

## Menu Bar

### Account Menu
- **Add** (F7) - Shows stub message box
- **Delete** (Del) - Shows stub message box (with selected account info if available)

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

## Next Steps
- Replace sample data with real TOTPAccount objects from AccountsManager
- Implement actual Add Account functionality
- Implement actual Delete Account functionality
- Add TOTP code display and countdown timer
