"""Tests for the help converter module."""

import tempfile
from pathlib import Path

import pytest

from simple_otp.core.help_converter import HelpConverter


class TestHelpConverter:
    """Test cases for HelpConverter."""

    @pytest.fixture
    def converter(self):
        """Create a HelpConverter instance."""
        return HelpConverter()

    @pytest.fixture
    def sample_md_file(self, tmp_path):
        """Create a sample Markdown file for testing."""
        md_content = """# Test Help

This is a **test** help file.

## Section 1

- Item 1
- Item 2

## Section 2

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |

> Important note

`code example`
"""
        md_file = tmp_path / "test.md"
        md_file.write_text(md_content, encoding="utf-8")
        return md_file

    def test_convert_md_to_html(self, converter, sample_md_file):
        """Test basic Markdown to HTML conversion."""
        html_file = converter.convert_md_to_html(sample_md_file)

        # Check that HTML file was created
        assert html_file.exists()

        # Check that HTML file is in temp/simple_otp directory
        temp_dir = Path(tempfile.gettempdir()) / "simple_otp"
        assert html_file.parent == temp_dir

        # Read and verify HTML content
        html_content = html_file.read_text(encoding="utf-8")

        # Verify HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert "<html" in html_content
        assert "picocss" in html_content
        assert "Test Help" in html_content
        assert "<strong>test</strong>" in html_content
        assert "<table>" in html_content
        assert "<blockquote>" in html_content
        assert "<code>" in html_content

        # Clean up
        html_file.unlink()

    def test_html_regenerated_each_time(self, converter, sample_md_file):
        """Test that HTML is regenerated on each call."""
        # First conversion
        html_file_1 = converter.convert_md_to_html(sample_md_file)
        content_1 = html_file_1.read_text(encoding="utf-8")

        # Second conversion (should regenerate)
        html_file_2 = converter.convert_md_to_html(sample_md_file)
        content_2 = html_file_2.read_text(encoding="utf-8")

        # Should be the same path
        assert html_file_1 == html_file_2
        # Content should be the same
        assert content_1 == content_2

        # Clean up
        html_file_2.unlink()

    def test_content_updates(self, converter, sample_md_file):
        """Test that updated content is reflected in HTML."""
        # First conversion
        html_file_1 = converter.convert_md_to_html(sample_md_file)
        content_1 = html_file_1.read_text(encoding="utf-8")
        assert "Test Help" in content_1

        # Modify the Markdown file
        sample_md_file.write_text("# Modified Content", encoding="utf-8")

        # Second conversion (should have new content)
        html_file_2 = converter.convert_md_to_html(sample_md_file)
        content_2 = html_file_2.read_text(encoding="utf-8")

        # Should contain modified content
        assert "Modified Content" in content_2
        assert "Test Help" not in content_2

        # Clean up
        html_file_2.unlink()

    def test_pico_css_integration(self, converter, sample_md_file):
        """Test that Pico CSS is properly integrated."""
        html_file = converter.convert_md_to_html(sample_md_file)
        html_content = html_file.read_text(encoding="utf-8")

        # Check for Pico CSS CDN link
        assert "picocss.com" in html_content or "cdn.jsdelivr.net" in html_content
        assert "pico" in html_content.lower()

        # Check for dark theme
        assert 'data-theme="dark"' in html_content

        # Clean up
        html_file.unlink()

    def test_real_help_files(self):
        """Test conversion of actual help files."""
        converter = HelpConverter()
        docs_path = Path(__file__).parent.parent / "simple_otp" / "docs"

        # Test Ukrainian help
        uk_md = docs_path / "uk-UA.md"
        if uk_md.exists():
            html_file = converter.convert_md_to_html(uk_md)
            assert html_file.exists()
            html_content = html_file.read_text(encoding="utf-8")
            assert "Simple OTP" in html_content
            # Clean up
            html_file.unlink()

        # Test English help
        en_md = docs_path / "en-US.md"
        if en_md.exists():
            html_file = converter.convert_md_to_html(en_md)
            assert html_file.exists()
            html_content = html_file.read_text(encoding="utf-8")
            assert "Simple OTP" in html_content
            # Clean up
            html_file.unlink()
