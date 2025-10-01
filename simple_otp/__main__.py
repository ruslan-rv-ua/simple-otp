"""Entry point for simple-otp application."""

import wx

from simple_otp.ui.main_window import MainWindow


def main():
    """Launch the Simple OTP application."""
    app = wx.App()
    frame = MainWindow(None)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
