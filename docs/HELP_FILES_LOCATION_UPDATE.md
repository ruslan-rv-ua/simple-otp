# Help Files Location Update

## Summary

Moved help files into the application package and organized temporary HTML files in a dedicated subdirectory.

## Changes

### 1. Help Files Location ✅

**Before:**
```
docs/
  ├── uk-UA.md
  └── en-US.md
```

**After:**
```
simple_otp/
  └── docs/
      ├── README.md
      ├── uk-UA.md
      └── en-US.md
```

**Benefits:**
- Help files are now part of the package distribution
- Included when package is installed
- No need to maintain separate docs folder
- Cleaner project structure

### 2. Temporary HTML Location ✅

**Before:**
```
%TEMP%\uk-UA.html
%TEMP%\en-US.html
```

**After:**
```
%TEMP%\simple_otp\uk-UA.html
%TEMP%\simple_otp\en-US.html
```

**Benefits:**
- Organized in dedicated subdirectory
- No clutter in temp root
- Easy to identify and clean up
- Professional file organization

## Code Changes

### `simple_otp/core/help_converter.py`
```python
# Create temporary HTML file in simple_otp subdirectory
temp_dir = Path(tempfile.gettempdir()) / "simple_otp"
temp_dir.mkdir(exist_ok=True)
html_path = temp_dir / f"{md_path.stem}.html"
```

### `simple_otp/ui/main_window.py`
```python
# Construct path to Markdown help file in simple_otp/docs/
docs_path = Path(__file__).parent.parent / "docs"
md_file_path = docs_path / f"{locale}.md"
```

### `tests/test_help_converter.py`
```python
# Updated test to use new location
docs_path = Path(__file__).parent.parent / "simple_otp" / "docs"
temp_dir = Path(tempfile.gettempdir()) / "simple_otp"
```

## File Structure

```
simple-otp/
├── docs/                          # Project documentation (dev only)
│   ├── README.md
│   ├── HELP_SYSTEM_REORGANIZATION.md
│   └── ... (other dev docs)
│
├── simple_otp/                    # Application package
│   ├── docs/                      # User help files (distributed)
│   │   ├── README.md
│   │   ├── uk-UA.md              # Ukrainian help
│   │   └── en-US.md              # English help
│   ├── core/
│   │   └── help_converter.py
│   └── ui/
│       └── main_window.py
│
└── tests/
    └── test_help_converter.py
```

## Temporary Files

When user opens help:
1. Reads `simple_otp/docs/{locale}.md`
2. Converts to HTML
3. Saves to `%TEMP%/simple_otp/{locale}.html`
4. Opens in browser

Example paths:
- Windows: `C:\Temp\simple_otp\uk-UA.html`
- Linux: `/tmp/simple_otp/uk-UA.html`

## Package Distribution

Help files are now included in the package:
```
simple_otp-0.1.0/
├── simple_otp/
│   ├── docs/           # ← Included in wheel/distribution
│   │   ├── uk-UA.md
│   │   └── en-US.md
│   └── ...
```

Users get help files automatically when installing the package.

## Testing

All tests updated and passing:
```bash
✅ 161 tests pass
✅ Help files found in simple_otp/docs/
✅ HTML created in %TEMP%/simple_otp/
✅ Verified visually in browser
```

## Migration Notes

### Old Files (can be removed)
- `docs/uk-UA.md` → Moved to `simple_otp/docs/uk-UA.md`
- `docs/en-US.md` → Already existed in `simple_otp/docs/en-US.md`
- `simple_otp/assets/help/` → Can be deleted (old HTML files)

### What to Keep
- `docs/` folder at root (for project documentation)
- `simple_otp/docs/` folder (for user help files)

## Benefits Summary

1. ✅ **Distribution**: Help files included in package
2. ✅ **Organization**: Temp files in dedicated subdirectory
3. ✅ **Clean**: No clutter in system temp root
4. ✅ **Professional**: Proper file organization
5. ✅ **Maintainable**: Clear separation of dev docs vs user help
6. ✅ **Standards**: Follows Python package best practices

## Commit Message

```
refactor(help): move help files into package and organize temp files

- Move help files from docs/ to simple_otp/docs/ (package distribution)
- Create temp HTML in %TEMP%/simple_otp/ subdirectory (organized)
- Update main_window to use package docs location
- Update tests to reflect new structure
- Add README to simple_otp/docs/ explaining user help system

Benefits:
- Help files distributed with package
- Organized temp file location
- Cleaner project structure
- Better separation of concerns (dev docs vs user help)
```
