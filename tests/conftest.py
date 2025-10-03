"""Pytest configuration for simple-otp tests."""

import pytest

from simple_otp.core.i18n import set_locale


@pytest.fixture(scope="session", autouse=True)
def setup_test_locale():
    """Set English locale for all tests."""
    set_locale("en-US")
