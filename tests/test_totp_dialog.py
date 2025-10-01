"""Test script for TOTP dialog functionality."""

import wx

from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount
from simple_otp.ui.totp_dialog import TOTPDialog, format_otp


def test_format_otp():
    """Test OTP formatting function."""
    # Test 6-digit code
    assert format_otp("123456") == "12 34 56"

    # Test 8-digit code
    assert format_otp("12345678") == "12 34 56 78"

    print("✓ format_otp tests passed")


def test_totp_dialog_manual():
    """Manual test for TOTP dialog - opens a GUI window."""
    app = wx.App()

    # Create a test account
    demo_password = "demo123"
    demo_secret = "JBSWY3DPEHPK3PXP"

    account = TOTPAccount.from_secret(
        name="test@example.com",
        secret=demo_secret,
        password=demo_password,
        issuer="Test Service",
        digits=6,
        digest=DigestAlgorithm.SHA1,
        interval=30,
    )

    # Create and show dialog
    dialog = TOTPDialog(None, account, demo_password)
    result = dialog.ShowModal()
    dialog.Destroy()

    print(f"✓ Dialog closed with result: {result}")


if __name__ == "__main__":
    # Run automated tests
    test_format_otp()

    # Run manual GUI test
    print("\nOpening TOTP dialog for manual testing...")
    print("- Check that current and next passwords are displayed")
    print("- Check that passwords are formatted as '12 34 56'")
    print("- Check that copy buttons work")
    print("- Check that progress bar counts down")
    test_totp_dialog_manual()
