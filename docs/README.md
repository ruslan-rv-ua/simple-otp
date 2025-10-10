# Help Documentation (Project Documentation)

This directory contains **project documentation** for Simple OTP development.

⚠️ **Note**: User-facing help files are located in `simple_otp/docs/` (inside the package).

## Directory Purpose

This `docs/` folder at the project root contains:
- Development documentation
- Implementation notes
- Technical specifications
- Change logs for specific features

## User Help Files Location

User help documentation is stored in the package:
- `simple_otp/docs/uk-UA.md` - Ukrainian help
- `simple_otp/docs/en-US.md` - English help

## How Help System Works

1. **Source Format**: Help files are stored as Markdown (`.md`) files in `simple_otp/docs/`
2. **Conversion**: When a user opens help, the Markdown is converted to HTML using `mistune`
3. **Styling**: HTML is styled with [Pico CSS](https://picocss.com/) (dark theme) from CDN
4. **Temporary Files**: HTML files are created in `%TEMP%/simple_otp/` subdirectory
5. **Browser**: Final HTML opens in the user's default web browser

## Adding New Locales

To add help for a new language:

1. Create a new file `[locale].md` in `simple_otp/docs/` directory (e.g., `de-DE.md`)
2. Translate the content from `en-US.md` or `uk-UA.md`
3. The application will automatically detect and use it based on user's locale setting

## Editing Help

To edit the help documentation:

1. Edit the appropriate `.md` file
2. Use standard Markdown syntax
3. Supported features:
   - Headings (h1-h6)
   - Lists (ordered and unordered)
   - Tables
   - Code blocks and inline code
   - Links
   - Blockquotes
   - Bold and italic text
   - Horizontal rules

## Technical Details

### HTML Conversion

The conversion is handled by `simple_otp.core.help_converter.HelpConverter`:

```python
from pathlib import Path
from simple_otp.core.help_converter import HelpConverter

converter = HelpConverter()
html_path = converter.convert_md_to_html(Path("simple_otp/docs/uk-UA.md"))
# HTML file created: %TEMP%\simple_otp\uk-UA.html
```

### Temporary Files

- Location: `%TEMP%/simple_otp/` subdirectory
- Filename format: `{locale}.html` (e.g., `uk-UA.html`)
- Full path example: `C:\Temp\simple_otp\uk-UA.html`
- Lifecycle: Created each time help is opened, overwriting previous version
- Cleanup: Managed by OS (temporary files are automatically cleaned)

### Styling

The generated HTML uses:
- **Pico CSS v2** from CDN (classless theme)
- **Dark theme** (`data-theme="dark"`)
- **No custom styles** - pure Pico CSS defaults
- **Responsive design** for different screen sizes
- **Accessibility features** (semantic HTML, proper contrast)

## Maintenance

- Keep help up-to-date with application features
- Maintain consistency between different language versions
- Test help rendering after major updates
- No cache management needed (files recreated each time)
