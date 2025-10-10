"""Utility functions for version management."""

from pathlib import Path


def get_app_version() -> str:
    """
    Get the application version from pyproject.toml.

    Returns:
        Version string, or "Unknown" if version cannot be determined
    """
    try:
        import tomllib

        # Get the path to pyproject.toml
        project_root = Path(__file__).parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "Unknown")
    except Exception:
        pass

    return "Unknown"
