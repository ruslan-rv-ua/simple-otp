"""Tests for version_utils."""

from pathlib import Path

from simple_otp.core.version_utils import get_app_version


def test_get_app_version():
    """Test getting application version."""
    version = get_app_version()

    # Should return a valid version or "Unknown"
    assert isinstance(version, str)
    assert len(version) > 0

    # If pyproject.toml exists, should return actual version
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"

    if pyproject_path.exists():
        # Version should match pattern like "0.1.0" or similar
        # At minimum, should not be "Unknown" if file exists
        assert version != "Unknown" or not pyproject_path.exists()
