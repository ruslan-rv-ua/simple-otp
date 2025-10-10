# Lang Attribute Implementation

## Summary

Added dynamic `lang` attribute to HTML help files based on the locale of the Markdown source file.

## Changes

### Modified: `simple_otp/core/help_converter.py`

#### Updated `_create_html_template()` method:
- Added `lang` parameter with default value `"en"`
- Updated HTML template to include `lang` attribute in `<html>` tag
- Template now generates: `<html lang="{lang}" data-theme="dark">`

#### Updated `convert_md_to_html()` method:
- Extracts language code from Markdown filename
- Converts locale format (e.g., `uk-UA` → `uk`, `en-US` → `en`)
- Passes language code to HTML template

## Implementation Details

### Language Code Extraction

```python
# From filename like "uk-UA.md" or "en-US.md"
locale = md_path.stem  # "uk-UA"
lang = locale.split("-")[0]  # "uk"
```

### HTML Template

```html
<html lang="{lang}" data-theme="dark">
```

## Examples

| Markdown File | `lang` Attribute |
|---------------|------------------|
| `uk-UA.md`    | `lang="uk"`      |
| `en-US.md`    | `lang="en"`      |
| `de-DE.md`    | `lang="de"`      |
| `fr-FR.md`    | `lang="fr"`      |

## Benefits

1. **Accessibility**: Screen readers can correctly identify document language
2. **SEO**: Search engines understand content language
3. **Browser Features**: Language-specific spell checking, hyphenation
4. **Standards Compliance**: Follows HTML5 best practices
5. **Automatic**: No manual configuration needed

## Testing

### Unit Tests
✅ All 161 tests pass

### Manual Verification
```python
from pathlib import Path
from simple_otp.core.help_converter import HelpConverter

c = HelpConverter()
html_uk = c.convert_md_to_html(Path('docs/uk-UA.md'))
content = html_uk.read_text(encoding='utf-8')

# Output: <html lang="uk" data-theme="dark">
```

## Commit Message

```
feat(help): add dynamic lang attribute based on locale

- Extract language code from Markdown filename (e.g., uk-UA → uk)
- Add lang parameter to HTML template
- Set lang attribute in <html> tag for accessibility
- Improves screen reader support and follows HTML5 standards

Benefits:
- Better accessibility for screen reader users
- Correct language identification for browsers
- Follows HTML5 best practices
```
