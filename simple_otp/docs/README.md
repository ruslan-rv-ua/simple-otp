# User Help Documentation

This directory contains user-facing help documentation for Simple OTP.

## Files

- `uk-UA.md` - Ukrainian help documentation
- `en-US.md` - English help documentation
- `AGENTS.md` - Instructions for AI agents (development)

## Format

Help files are written in Markdown and automatically converted to HTML when users open the help system.

## Adding New Locales

To add help for a new language:

1. Create a new file `{locale}.md` in this directory
   - Use format: `{language}-{REGION}.md` (e.g., `de-DE.md`, `fr-FR.md`)
2. Translate content from `en-US.md` or `uk-UA.md`
3. Follow the same structure and formatting
4. The application will automatically detect and use it based on user's locale setting

## Editing Help

When editing help documentation:

1. Use standard Markdown syntax
2. Maintain consistent structure across locales
3. Keep translations synchronized
4. Test rendering by opening help in the application

## Technical Details

- **Location**: Inside the `simple_otp` package (included in distribution)
- **Conversion**: Markdown → HTML using `mistune`
- **Styling**: Pico CSS (dark theme)
- **Output**: HTML files in `%TEMP%/simple_otp/`
- **Language detection**: Based on filename (e.g., `uk-UA.md` → `lang="uk"`)

## Supported Markdown Features

- Headings (h1-h6)
- Lists (ordered, unordered)
- Tables
- Code blocks and inline code
- Links
- Blockquotes
- Bold and italic text
- Horizontal rules
- Task lists
- Strikethrough

## File Naming Convention

Use the format: `{language}-{REGION}.md`

Examples:
- `uk-UA.md` - Ukrainian (Ukraine)
- `en-US.md` - English (United States)
- `en-GB.md` - English (United Kingdom)
- `de-DE.md` - German (Germany)
- `fr-FR.md` - French (France)
