"""TOTP Dialog for displaying current and next OTP codes."""

import time

import pyperclip
import wx

from simple_otp.core.i18n import _
from simple_otp.core.settings_manager import SettingsManager
from simple_otp.models.totp_account import TOTPAccount
from simple_otp.ui.audio_player import audio_player

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

    def __init__(
        self,
        parent,
        account: TOTPAccount,
        password: str,
        settings_manager: SettingsManager,
    ):
        """
        Initialize the TOTP dialog.

        Args:
            parent: Parent window
            account: The TOTP account to display codes for
            password: Password to decrypt the account secret
            settings_manager: Settings manager for audio and auto-copy settings
        """
        super().__init__(
            parent,
            title=_("totp_dialog.title").format(name=account.get_display_name()),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.account = account
        self.password = password
        self.totp = account.get_totp(password)
        self.settings_manager = settings_manager

        # Use global audio player instance
        self.audio_player = audio_player
        self.sound_played_for_interval = False
        self.last_copied_otp = None  # Track last auto-copied OTP to avoid duplicates

        # Create UI
        self._create_ui()

        # Start the timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self.timer)
        self.timer.Start(TIMER_INTERVAL_MS)

        # Initial update
        self._update_codes_and_progress()

        # Center the dialog
        self.CenterOnParent()

    def _create_ui(self):
        """Create the dialog UI layout."""
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Current OTP section
        current_label = wx.StaticText(panel, label=_("totp_dialog.current_label"))
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

        self.current_copy_btn = wx.Button(
            panel, label=_("totp_dialog.button_copy_current")
        )
        self.current_copy_btn.Bind(wx.EVT_BUTTON, self._on_copy_current)
        current_sizer.Add(self.current_copy_btn, 0, wx.ALL, 5)

        main_sizer.Add(current_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Next OTP section
        next_label = wx.StaticText(panel, label=_("totp_dialog.next_label"))
        main_sizer.Add(next_label, 0, wx.ALL, 5)

        next_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.next_text = wx.TextCtrl(
            panel, style=wx.TE_READONLY | wx.TE_CENTER, size=wx.Size(200, -1)
        )
        self.next_text.AcceptsFocusFromKeyboard = lambda: True
        self.next_text.SetName("next")
        self.next_text.SetFont(font)
        next_sizer.Add(self.next_text, 1, wx.ALL | wx.EXPAND, 5)

        self.next_copy_btn = wx.Button(panel, label=_("totp_dialog.button_copy_next"))
        self.next_copy_btn.Bind(wx.EVT_BUTTON, self._on_copy_next)
        next_sizer.Add(self.next_copy_btn, 0, wx.ALL, 5)

        main_sizer.Add(next_sizer, 0, wx.ALL | wx.EXPAND, 5)

        # Progress bar
        progress_label = wx.StaticText(
            panel, label=_("totp_dialog.time_remaining_label")
        )
        main_sizer.Add(progress_label, 0, wx.ALL, 5)

        self.progress_bar = wx.Gauge(panel, range=100, style=wx.GA_HORIZONTAL)
        main_sizer.Add(self.progress_bar, 0, wx.ALL | wx.EXPAND, 5)

        # Close button
        close_btn = wx.Button(panel, wx.ID_CLOSE, _("totp_dialog.button_close"))
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

        # Get audio settings
        play_warning = self.settings_manager.get("audio.play_warning_sound", True)
        warning_seconds = self.settings_manager.get("audio.warning_sound_seconds", 5)

        # Play warning sound when below threshold (only once per interval)
        if (
            time_remaining < warning_seconds
            and not self.sound_played_for_interval
            and play_warning
        ):
            if self.audio_player:
                try:
                    self.audio_player.play("under_5_seconds.wav")
                except (FileNotFoundError, RuntimeError):
                    pass
            self.sound_played_for_interval = True
        elif time_remaining >= warning_seconds:
            # Reset flag when we're back above threshold (new interval started)
            self.sound_played_for_interval = False

        # Auto-copy on password update
        auto_copy_enabled = self.settings_manager.get(
            "behavior.auto_copy_on_update", False
        )
        if auto_copy_enabled and current_otp != self.last_copied_otp:
            # New OTP generated, auto-copy it
            pyperclip.copy(current_otp)
            self.last_copied_otp = current_otp

            # Play sound if enabled
            play_copied_sound = self.settings_manager.get(
                "audio.play_password_copied_sound", True
            )
            if play_copied_sound and self.audio_player:
                try:
                    self.audio_player.play("password_copied.wav")
                except (FileNotFoundError, RuntimeError):
                    pass

    def _on_timer(self, event):
        """Handle timer event to update codes and progress."""
        self._update_codes_and_progress()

    def _on_copy_current(self, event):
        """Copy current OTP to clipboard (without spaces)."""
        otp_code = self.current_text.GetValue().replace(" ", "")
        pyperclip.copy(otp_code)
        # Play sound notification if enabled
        play_sound = self.settings_manager.get("audio.play_password_copied_sound", True)
        if play_sound and self.audio_player:
            try:
                self.audio_player.play("password_copied.wav")
            except (FileNotFoundError, RuntimeError) as e:
                # Log the error but don't interrupt the UI
                print(f"Warning: Failed to play sound: {e}")

    def _on_copy_next(self, event):
        """Copy next OTP to clipboard (without spaces)."""
        otp_code = self.next_text.GetValue().replace(" ", "")
        pyperclip.copy(otp_code)
        # Play sound notification if enabled
        play_sound = self.settings_manager.get("audio.play_password_copied_sound", True)
        if play_sound and self.audio_player:
            try:
                self.audio_player.play("password_copied.wav")
            except (FileNotFoundError, RuntimeError) as e:
                # Log the error but don't interrupt the UI
                print(f"Warning: Failed to play sound: {e}")

    def _on_close(self, event):
        """Handle close button click."""
        self.timer.Stop()
        self.EndModal(wx.ID_CLOSE)

    def Destroy(self):
        """Clean up timer when dialog is destroyed."""
        if hasattr(self, "timer") and self.timer.IsRunning():
            self.timer.Stop()
        return super().Destroy()
