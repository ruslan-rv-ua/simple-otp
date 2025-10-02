"""TOTP Dialog for displaying current and next OTP codes."""

import time

import pyperclip
import wx

from simple_otp.models.totp_account import TOTPAccount

TIMER_INTERVAL_MS = 100  # Update every 100ms for smooth progress bar


def format_otp(otp_code: str) -> str:
    """
    Format OTP code by grouping digits by 2.

    Args:
        otp_code: The OTP code string (e.g., "123456" or "12345678")

    Returns:
        Formatted string with spaces (e.g., "12 34 56" or "12 34 56 78")
    """
    return " ".join([otp_code[i : i + 2] for i in range(0, len(otp_code), 2)])


class TOTPDialog(wx.Dialog):
    """Dialog displaying current and next TOTP codes with countdown."""

    def __init__(self, parent, account: TOTPAccount, password: str):
        """
        Initialize the TOTP dialog.

        Args:
            parent: Parent window
            account: The TOTP account to display codes for
            password: Password to decrypt the account secret
        """
        super().__init__(
            parent,
            title=f"TOTP - {account.get_display_name()}",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.account = account
        self.password = password
        self.totp = account.get_totp(password)

        # Create UI
        self._create_ui()

        # Start the timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.timer.Start(self.TIMER_INTERVAL_MS)

        # Initial update
        self._update_codes_and_progress()

        # Center the dialog
        self.CenterOnParent()

    def _create_ui(self):
        """Create the dialog UI layout."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Current OTP section
        current_label = wx.StaticText(panel, label="Current")
        main_sizer.Add(current_label, 0, wx.ALL, 5)

        current_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.current_text = wx.TextCtrl(
            panel, style=wx.TE_READONLY | wx.TE_CENTER, size=wx.Size(200, -1)
        )
        self.current_text.AcceptsFocusFromKeyboard = lambda: True
        # Make text larger and bold
        font = self.current_text.GetFont()
        font.PointSize = 14
        font = font.Bold()
        self.current_text.SetFont(font)
        current_sizer.Add(self.current_text, 1, wx.ALL | wx.EXPAND, 5)

        self.current_copy_btn = wx.Button(panel, label="Copy Current")
        self.current_copy_btn.Bind(wx.EVT_BUTTON, self._on_copy_current)
        current_sizer.Add(self.current_copy_btn, 0, wx.ALL, 5)

        main_sizer.Add(current_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Next OTP section
        next_label = wx.StaticText(panel, label="Next")
        main_sizer.Add(next_label, 0, wx.ALL, 5)

        next_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.next_text = wx.TextCtrl(
            panel, style=wx.TE_READONLY | wx.TE_CENTER, size=wx.Size(200, -1)
        )
        self.next_text.AcceptsFocusFromKeyboard = lambda: True
        self.next_text.SetName("next")
        self.next_text.SetFont(font)
        next_sizer.Add(self.next_text, 1, wx.ALL | wx.EXPAND, 5)

        self.next_copy_btn = wx.Button(panel, label="Copy Next")
        self.next_copy_btn.Bind(wx.EVT_BUTTON, self._on_copy_next)
        next_sizer.Add(self.next_copy_btn, 0, wx.ALL, 5)

        main_sizer.Add(next_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Progress bar
        progress_label = wx.StaticText(panel, label="Time Remaining:")
        main_sizer.Add(progress_label, 0, wx.ALL, 5)

        self.progress_bar = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        main_sizer.Add(self.progress_bar, 0, wx.ALL | wx.EXPAND, 5)

        # Close button
        close_btn = wx.Button(panel, wx.ID_CLOSE, "Close")
        close_btn.Bind(wx.EVT_BUTTON, self._on_close)
        main_sizer.Add(close_btn, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        panel.SetSizer(main_sizer)

        # Fit dialog to content
        main_sizer.Fit(self)
        self.SetMinSize(self.GetSize())

    def _update_codes_and_progress(self):
        """Update the OTP codes and progress bar."""
        current_time = time.time()

        # Get current and next OTP codes
        current_otp = self.totp.now()

        # Calculate next OTP by getting OTP for next interval
        next_time = int(current_time + self.account.interval)
        next_otp = self.totp.at(next_time)

        # Update text controls with formatted codes
        self.current_text.SetValue(format_otp(current_otp))
        self.next_text.SetValue(format_otp(next_otp))

        # Calculate progress (time remaining in current interval)
        time_in_interval = current_time % self.account.interval
        time_remaining = self.account.interval - time_in_interval
        progress_percent = int((time_remaining / self.account.interval) * 100)

        # Update progress bar (it goes down as time progresses)
        self.progress_bar.SetValue(progress_percent)

    def _on_timer(self, event):
        """Handle timer event to update codes and progress."""
        self._update_codes_and_progress()

    def _on_copy_current(self, event):
        """Copy current OTP to clipboard (without spaces)."""
        otp_code = self.current_text.GetValue().replace(" ", "")
        pyperclip.copy(otp_code)
        wx.MessageBox(
            "Current password copied to clipboard!",
            "Copied",
            wx.OK | wx.ICON_INFORMATION,
            self,
        )

    def _on_copy_next(self, event):
        """Copy next OTP to clipboard (without spaces)."""
        otp_code = self.next_text.GetValue().replace(" ", "")
        pyperclip.copy(otp_code)
        wx.MessageBox(
            "Next password copied to clipboard!",
            "Copied",
            wx.OK | wx.ICON_INFORMATION,
            self,
        )

    def _on_close(self, event):
        """Handle close button click."""
        self.timer.Stop()
        self.EndModal(wx.ID_CLOSE)

    def Destroy(self):
        """Clean up timer when dialog is destroyed."""
        if hasattr(self, "timer") and self.timer.IsRunning():
            self.timer.Stop()
        return super().Destroy()
