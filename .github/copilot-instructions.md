# simple-otp - AI Coding Agent Instructions

## Project Overview
Desktop application for generating TOTP (Time-based One-Time Passwords) using wxPython GUI. Built with modern Python packaging (`pyproject.toml`) and managed with **uv**. The `pyproject.toml` file in the repository is the single source of truth for the project's metadata, Python requirement, and declared runtime dependencies — use it to verify the runtime Python version and which packages to install.

Based on the current `pyproject.toml`:
- Python requirement: `requires-python = ">=3.13"`
- Declared dependencies: `cryptography>=46.0.2`, `objectlistview3>=1.3.5`, `pyotp>=2.9.0`, `wxpython>=4.2.3`

## Architecture & Structure
```
simple-otp/
├── pyproject.toml          # PEP 621 project metadata & dependencies (authoritative)
├── simple_otp/
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point - launches GUI
│   ├── ui/                 # wxPython GUI components
│   ├── core/               # TOTP generation logic (PyOTP)
│   └── models/             # Data models for OTP accounts
```

## Technology Stack
- **GUI Framework**: wxPython (native desktop UI)
- **List Control**: ObjectListView3 (enhanced wx.ListCtrl)
- **OTP Library**: PyOTP (https://github.com/pyauth/pyotp)
- **Package Manager**: uv (NOT pip/poetry)
- **Build Backend**: Hatchling

## Development Setup
Check `pyproject.toml` for the authoritative Python version and dependency list before creating an environment or adding packages. Use `uv` to manage packages and run the project in the managed environment:
```cmd
REM Add or update dependencies (updates pyproject and lock file)
uv add <package>

REM Install from lockfile / sync environment
uv sync

REM Run the app in the uv-managed environment
uv run python -m simple_otp
```

## Key Conventions

### Entry Point Pattern
- **Primary entry**: `__main__.py` (run as `python -m simple_otp`) — the package also exposes a script entry in `pyproject.toml` (`simple-otp = "simple_otp:main"`) for convenience in some environments.
- `__main__.py` initializes wxPython app and launches main window
- Example structure:
  ```python
  # __main__.py
  import wx
  from simple_otp.ui.main_window import MainWindow
  
  def main():
      app = wx.App()
      frame = MainWindow(None)
      frame.Show()
      app.MainLoop()
  
  if __name__ == "__main__":
      main()
  ```

### TOTP Implementation
- Use **PyOTP library** for TOTP generation: `pyotp.TOTP(secret).now()`
- Reference: https://pyauth.github.io/pyotp/#pyotp.totp.TOTP.now
- Store secrets securely (consider encryption for production)

### Security: salts and secrets
When you need a cryptographically strong random salt (for key derivation or storage), use Python's `secrets` module. Example:

```python
import secrets

# generate a cryptographically secure 16-byte salt
salt = secrets.token_bytes(16)
```

This produces a 16-byte (128-bit) salt suitable for use with key derivation functions (e.g., PBKDF2, scrypt) or as a nonce. Persist salts and secrets securely; do not hard-code them in source. For production, encrypt secrets at rest and protect access to any storage used.

### GUI Components
- **wxPython** for cross-platform native UI (Windows primary target)
- **ObjectListView3** for displaying OTP account lists with sorting/filtering
- Keep UI logic separate from business logic (`ui/` vs `core/`)

### Dependency Management
- **Use uv exclusively** for package management:
  ```cmd
  uv add <package>    REM Add dependencies
  uv sync             REM Sync from lock file
  uv run <command>    REM Run in managed environment
  ```
- Add or verify dependencies in `pyproject.toml` → `dependencies` (see file for current pinned versions)

### Commit Conventions
- **Conventional Commits** format: `<type>(<scope>): <description>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- Examples:
  ```
  feat(totp): implement TOTP generation with PyOTP
  fix(ui): correct timer refresh for OTP countdown
  docs(readme): add installation instructions
  ```

## Implementation Priority
1. TOTP core functionality using PyOTP
2. Basic wxPython GUI with account list (ObjectListView3)
3. Add/Edit/Delete account management
4. Countdown timer and auto-refresh for codes
5. Data persistence (file-based storage initially)

## Critical Notes
- **Windows development environment** (cmd.exe) - primary target platform
- Entry point is `__main__.py` (package execution), NOT console script
- Use **uv** for ALL dependency operations (not pip/poetry)
- Follow **Conventional Commits** for all git commits
- This is a **desktop GUI app**, not a CLI tool
- Code syntax must be compatible with Python 3.13 and newer; avoid using features or APIs that are deprecated in Python 3.13.
