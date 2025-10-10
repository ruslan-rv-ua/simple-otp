"""Help converter module for converting Markdown help files to HTML."""

import tempfile
from pathlib import Path

import mistune


class HelpConverter:
    """Converts Markdown help files to HTML with Pico CSS styling."""

    def _create_html_template(
        self, content: str, title: str = "Simple OTP", lang: str = "en"
    ) -> str:
        """
        Create complete HTML document with Pico CSS.

        Args:
            content: HTML content (body)
            title: Page title
            lang: Language code for HTML lang attribute

        Returns:
            Complete HTML document as string
        """
        return f"""<!DOCTYPE html>
<html lang="{lang}" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.classless.min.css">
</head>
<body>
    {content}
</body>
</html>"""

    def convert_md_to_html(self, md_path: Path) -> Path:
        """
        Convert a Markdown file to HTML.

        Args:
            md_path: Path to the Markdown file

        Returns:
            Path to the generated HTML file in temp directory
        """
        # Read Markdown content
        md_content = md_path.read_text(encoding="utf-8")

        # Convert Markdown to HTML
        markdown = mistune.create_markdown(
            escape=False,
            plugins=["table", "url", "strikethrough", "task_lists"],
        )
        html_content = str(markdown(md_content))

        # Extract title from first h1 heading or use default
        title = "Simple OTP"
        if html_content.startswith("<h1>"):
            end_h1 = html_content.find("</h1>")
            if end_h1 != -1:
                title = html_content[4:end_h1]

        # Extract language from filename (e.g., "uk-UA" -> "uk")
        locale = md_path.stem  # e.g., "uk-UA" or "en-US"
        lang = locale.split("-")[0] if "-" in locale else locale

        # Wrap in complete HTML template
        full_html = self._create_html_template(html_content, title, lang)

        # Create temporary HTML file in simple_otp subdirectory
        temp_dir = Path(tempfile.gettempdir()) / "simple_otp"
        temp_dir.mkdir(exist_ok=True)
        html_path = temp_dir / f"{md_path.stem}.html"

        # Write HTML content
        html_path.write_text(full_html, encoding="utf-8")

        return html_path
