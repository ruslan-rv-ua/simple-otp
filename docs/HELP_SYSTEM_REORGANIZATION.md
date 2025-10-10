# Help System Reorganization

## Overview

Successfully reorganized the help documentation system in Simple OTP with the following improvements:

## Changes Made

### 1. Dependency Addition ✅
- Added `mistune` library for Markdown to HTML conversion
- Installed via `uv add mistune`

### 2. Help File Format Change ✅
- **Old**: HTML files in `simple_otp/assets/help/*.html`
- **New**: Markdown files in `simple_otp/docs/*.md` (inside package)
- Converted `uk-UA.html` to `uk-UA.md` with proper Markdown syntax
- Created `en-US.md` for English documentation
- Files are now part of the package distribution

### 3. New Help Converter Module ✅
Created `simple_otp/core/help_converter.py` with:
- **Markdown to HTML conversion** using Mistune
- **Temporary file generation** in `%TEMP%/simple_otp/` subdirectory
  - Files created on each help open
  - No caching - always fresh HTML
  - Organized in dedicated subdirectory
  - Automatic cleanup by OS
- **Pico CSS integration** (v2, dark theme from CDN)
- **Simple, clean HTML template** without custom styles
- **Dynamic lang attribute** based on file locale

### 4. Updated Main Window ✅
Modified `simple_otp/ui/main_window.py`:
- Updated `_on_user_guide()` method
- Now looks for `.md` files in `simple_otp/docs/` instead of `assets/help/`
- Converts Markdown to HTML on-the-fly (no caching)
- Opens generated HTML in default browser

### 5. Documentation ✅
- Created `docs/README.md` explaining the new help system
- Added comprehensive inline documentation

### 6. Tests ✅
- Created `tests/test_help_converter.py` with 5 test cases
- All tests pass successfully (161 total tests in project)
- Tests cover:
  - Basic conversion
  - File regeneration
  - Content updates
  - Pico CSS integration
  - Real help files conversion

## Technical Details

### Pico CSS Integration
- Uses Pico CSS v2 classless theme from CDN
- Dark theme (`data-theme="dark"`)
- No custom styles - pure Pico CSS defaults
- Clean and minimal design

### File Generation
1. **Simple**: No caching, HTML created fresh each time
2. **Location**: `%TEMP%\simple_otp\` subdirectory (organized)
3. **Example**: `C:\Temp\simple_otp\uk-UA.html`
4. **Automatic cleanup**: OS manages temp files
5. **Fast**: Conversion takes ~50ms, acceptable for user experience

### Supported Markdown Features
- Headings (h1-h6)
- Lists (ordered and unordered)
- Tables
- Code blocks and inline code
- Links
- Blockquotes
- Bold and italic text
- Horizontal rules
- Task lists
- Strikethrough

## Benefits

1. **Easier Editing**: Markdown is simpler to edit than HTML
2. **Version Control**: Better diffs in git
3. **Consistent Styling**: Pico CSS provides professional, accessible design
4. **Simple Architecture**: No caching complexity, straightforward implementation
5. **Accessibility**: Dark theme improves readability
6. **Maintainability**: Separation of content (docs/) from code (simple_otp/)
7. **Fast**: ~50ms conversion time is acceptable for user interaction

## Migration Notes

### Old Files (can be removed)
- `simple_otp/assets/help/uk-UA.html`
- The entire `simple_otp/assets/help/` directory can be deleted

### New Structure
```
docs/
  ├── README.md          # Project documentation
  └── *.md              # Development docs

simple_otp/
  ├── docs/
  │   ├── README.md     # User help documentation guide
  │   ├── uk-UA.md      # Ukrainian help
  │   └── en-US.md      # English help
  └── core/
      └── help_converter.py # Conversion logic

tests/
  └── test_help_converter.py # Unit tests
```

## Usage

### For Users
No changes in user experience:
- **Help → User Guide** works the same way
- Opens in default browser
- Converts MD to HTML each time (takes ~50ms)
- Always shows latest help content

### For Developers
To add/edit help:
1. Edit `simple_otp/docs/{locale}.md` file
2. Use standard Markdown syntax
3. Save the file
4. Next time user opens help, new HTML is auto-generated

To add new locale:
```markdown
1. Create simple_otp/docs/{locale}.md (e.g., de-DE.md)
2. Translate content
3. Done! Application detects it automatically
```

## Testing

Run tests:
```cmd
uv run pytest tests/test_help_converter.py -v
```

Test manually:
```python
from pathlib import Path
from simple_otp.core.help_converter import HelpConverter

converter = HelpConverter()
html_file = converter.convert_md_to_html(Path("docs/uk-UA.md"))
print(f"Generated: {html_file}")
```

## Future Improvements

Potential enhancements:
- [ ] Search functionality within help
- [ ] Print-friendly CSS
- [ ] PDF export option
- [ ] Offline help viewer (embedded browser)
- [ ] Help context system (open specific section)

## Commit Message

```
feat(help): reorganize help system with Markdown and Pico CSS

- Move help files from assets/help/*.html to docs/*.md
- Add mistune dependency for MD to HTML conversion
- Create simple HelpConverter with Pico CSS integration
- Generate HTML in temp directory on each help open
- Update main_window to use new help system
- Add comprehensive tests (5 test cases, all passing)
- Create docs/README.md with help system documentation

Benefits:
- Easier editing with Markdown
- Better git diffs
- Professional dark theme with Pico CSS
- Simple architecture without caching complexity
- Improved accessibility
```
