"""Pytest configuration for simple-otp tests."""

import pytest

from simple_otp.core.i18n import init_i18n


@pytest.fixture(scope="session", autouse=True)
def setup_test_locale():
    """Set English locale for all tests."""
    # Reinitialize i18n with English locale to ensure consistent test environment
    init_i18n(locale="en-US", auto_detect=False)
