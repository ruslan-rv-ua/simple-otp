"""Settings dialog for simple-otp application."""

import wx

from simple_otp.core.settings_manager import SettingsManager


class SettingsDialog(wx.Dialog):
    """Dialog for managing application settings."""

    def __init__(self, parent, settings_manager: SettingsManager):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent window
            settings_manager: SettingsManager instance to read/write settings
        """
        super().__init__(
            parent,
            title="Settings",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )

        self.settings_manager = settings_manager

        # Create the UI
        self._create_ui()

        # Load current settings
        self._load_settings()

        # Size the dialog
        self.SetSize(500, 400)
        self.CenterOnParent()

    def _create_ui(self):
        """Create the dialog UI."""
        # Main panel
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Create notebook for settings categories
        self.notebook = wx.Notebook(panel)

        # Add pages
        self._create_ui_page()
        self._create_security_page()
        self._create_totp_page()
        self._create_audio_page()

        main_sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 10)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.reset_button = wx.Button(panel, label="Reset to Defaults")
        self.reset_button.Bind(wx.EVT_BUTTON, self._on_reset)
        button_sizer.Add(self.reset_button, 0, wx.ALL, 5)

        button_sizer.AddStretchSpacer()

        ok_button = wx.Button(panel, wx.ID_OK, "OK")
        ok_button.Bind(wx.EVT_BUTTON, self._on_ok)
        button_sizer.Add(ok_button, 0, wx.ALL, 5)

        cancel_button = wx.Button(panel, wx.ID_CANCEL, "Cancel")
        button_sizer.Add(cancel_button, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(main_sizer)

    def _create_ui_page(self):
        """Create the UI settings page."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Theme setting
        theme_label = wx.StaticText(panel, label="Theme:")
        sizer.Add(theme_label, 0, wx.ALL, 5)

        self.theme_choice = wx.Choice(panel, choices=["Default"])
        self.theme_choice.SetSelection(0)
        self.theme_choice.Enable(False)  # Disabled - not implemented
        sizer.Add(self.theme_choice, 0, wx.ALL | wx.EXPAND, 5)

        # Font size setting
        font_size_label = wx.StaticText(panel, label="Font Size:")
        sizer.Add(font_size_label, 0, wx.ALL, 5)

        self.font_size_spin = wx.SpinCtrl(panel, value="10", min=8, max=24)
        self.font_size_spin.Enable(False)  # Disabled - not implemented
        sizer.Add(self.font_size_spin, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, "User Interface")

    def _create_security_page(self):
        """Create the security settings page."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Auto-copy on update checkbox
        self.auto_copy_on_update_check = wx.CheckBox(
            panel,
            label="Automatically copy password to clipboard when it updates",
        )
        sizer.Add(self.auto_copy_on_update_check, 0, wx.ALL, 5)

        # Auto-copy to clipboard
        self.auto_copy_check = wx.CheckBox(
            panel, label="Automatically copy TOTP to clipboard"
        )
        self.auto_copy_check.Enable(False)  # Disabled - not implemented
        sizer.Add(self.auto_copy_check, 0, wx.ALL, 5)

        # Clear clipboard
        self.clear_clipboard_check = wx.CheckBox(
            panel, label="Clear clipboard after timeout"
        )
        self.clear_clipboard_check.Enable(False)  # Disabled - not implemented
        sizer.Add(self.clear_clipboard_check, 0, wx.ALL, 5)

        # Clipboard timeout
        timeout_label = wx.StaticText(panel, label="Clipboard timeout (seconds):")
        sizer.Add(timeout_label, 0, wx.ALL, 5)

        self.clipboard_timeout_spin = wx.SpinCtrl(panel, value="30", min=5, max=300)
        self.clipboard_timeout_spin.Enable(False)  # Disabled - not implemented
        sizer.Add(self.clipboard_timeout_spin, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, "Security")

    def _create_totp_page(self):
        """Create the TOTP settings page."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Default digits
        digits_label = wx.StaticText(panel, label="Default number of digits:")
        sizer.Add(digits_label, 0, wx.ALL, 5)

        self.digits_choice = wx.Choice(panel, choices=["6", "7", "8"])
        self.digits_choice.SetSelection(0)
        self.digits_choice.Enable(False)  # Disabled - not implemented
        sizer.Add(self.digits_choice, 0, wx.ALL | wx.EXPAND, 5)

        # Default interval
        interval_label = wx.StaticText(panel, label="Default interval (seconds):")
        sizer.Add(interval_label, 0, wx.ALL, 5)

        self.interval_spin = wx.SpinCtrl(panel, value="30", min=15, max=120)
        self.interval_spin.Enable(False)  # Disabled - not implemented
        sizer.Add(self.interval_spin, 0, wx.ALL | wx.EXPAND, 5)

        # Default digest
        digest_label = wx.StaticText(panel, label="Default hash algorithm:")
        sizer.Add(digest_label, 0, wx.ALL, 5)

        self.digest_choice = wx.Choice(panel, choices=["SHA1", "SHA256", "SHA512"])
        self.digest_choice.SetSelection(0)
        self.digest_choice.Enable(False)  # Disabled - not implemented
        sizer.Add(self.digest_choice, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, "TOTP Defaults")

    def _create_audio_page(self):
        """Create the audio settings page."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Play password copied sound checkbox
        self.play_password_copied_check = wx.CheckBox(
            panel, label="Play sound when password is copied"
        )
        sizer.Add(self.play_password_copied_check, 0, wx.ALL, 5)

        # Play warning sound checkbox
        self.play_warning_check = wx.CheckBox(
            panel, label="Play warning sound before password expires"
        )
        sizer.Add(self.play_warning_check, 0, wx.ALL, 5)

        # Warning sound seconds - label and spinctrl in horizontal layout
        warning_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.warning_seconds_label = wx.StaticText(
            panel, label="Play warning sound (seconds before expiration):"
        )
        warning_sizer.Add(
            self.warning_seconds_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5
        )

        self.warning_seconds_spin = wx.SpinCtrl(
            panel, value="5", min=1, max=15, size=wx.Size(60, -1)
        )
        warning_sizer.Add(self.warning_seconds_spin, 0, wx.ALL, 5)

        sizer.Add(warning_sizer, 0, wx.ALL, 0)

        # Bind checkbox to enable/disable spin control
        self.play_warning_check.Bind(wx.EVT_CHECKBOX, self._on_warning_check_changed)

        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, "Audio")

    def _load_settings(self):
        """Load settings from the settings manager into the UI controls."""
        # UI settings
        theme = self.settings_manager.get("ui.theme", "default")
        if theme == "default":
            self.theme_choice.SetSelection(0)

        font_size = self.settings_manager.get("ui.font_size", 10)
        self.font_size_spin.SetValue(font_size)

        # Security settings
        auto_copy = self.settings_manager.get("security.auto_copy", True)
        self.auto_copy_check.SetValue(auto_copy)

        clear_clipboard = self.settings_manager.get("security.clear_clipboard", True)
        self.clear_clipboard_check.SetValue(clear_clipboard)

        clipboard_timeout = self.settings_manager.get("security.clipboard_timeout", 30)
        self.clipboard_timeout_spin.SetValue(clipboard_timeout)

        # TOTP settings
        digits = self.settings_manager.get("totp.default_digits", 6)
        self.digits_choice.SetSelection(digits - 6)  # 6->0, 7->1, 8->2

        interval = self.settings_manager.get("totp.default_interval", 30)
        self.interval_spin.SetValue(interval)

        digest = self.settings_manager.get("totp.default_digest", "SHA1")
        digest_map = {"SHA1": 0, "SHA256": 1, "SHA512": 2}
        self.digest_choice.SetSelection(digest_map.get(digest, 0))

        # Audio settings
        play_password_copied = self.settings_manager.get(
            "audio.play_password_copied_sound", True
        )
        self.play_password_copied_check.SetValue(play_password_copied)

        play_warning = self.settings_manager.get("audio.play_warning_sound", True)
        self.play_warning_check.SetValue(play_warning)

        warning_seconds = self.settings_manager.get("audio.warning_sound_seconds", 5)
        self.warning_seconds_spin.SetValue(warning_seconds)

        # Enable/disable warning spin control based on checkbox
        self.warning_seconds_spin.Enable(play_warning)
        self.warning_seconds_label.Enable(play_warning)

        # Security - Auto-copy settings
        auto_copy_on_update = self.settings_manager.get(
            "audio.auto_copy_on_update", False
        )
        self.auto_copy_on_update_check.SetValue(auto_copy_on_update)

    def _save_settings(self):
        """Save settings from UI controls to the settings manager."""
        # UI settings
        theme = "default" if self.theme_choice.GetSelection() == 0 else "default"
        self.settings_manager.set("ui.theme", theme)

        font_size = self.font_size_spin.GetValue()
        self.settings_manager.set("ui.font_size", font_size)

        # Security settings
        auto_copy = self.auto_copy_check.GetValue()
        self.settings_manager.set("security.auto_copy", auto_copy)

        clear_clipboard = self.clear_clipboard_check.GetValue()
        self.settings_manager.set("security.clear_clipboard", clear_clipboard)

        clipboard_timeout = self.clipboard_timeout_spin.GetValue()
        self.settings_manager.set("security.clipboard_timeout", clipboard_timeout)

        # TOTP settings
        digits = self.digits_choice.GetSelection() + 6  # 0->6, 1->7, 2->8
        self.settings_manager.set("totp.default_digits", digits)

        interval = self.interval_spin.GetValue()
        self.settings_manager.set("totp.default_interval", interval)

        digest_options = ["SHA1", "SHA256", "SHA512"]
        digest = digest_options[self.digest_choice.GetSelection()]
        self.settings_manager.set("totp.default_digest", digest)

        # Audio settings
        play_password_copied = self.play_password_copied_check.GetValue()
        self.settings_manager.set(
            "audio.play_password_copied_sound", play_password_copied
        )

        play_warning = self.play_warning_check.GetValue()
        self.settings_manager.set("audio.play_warning_sound", play_warning)

        warning_seconds = self.warning_seconds_spin.GetValue()
        self.settings_manager.set("audio.warning_sound_seconds", warning_seconds)

        auto_copy_on_update = self.auto_copy_on_update_check.GetValue()
        self.settings_manager.set("audio.auto_copy_on_update", auto_copy_on_update)

        # Save to file
        self.settings_manager.save()

    def _on_ok(self, event):
        """Handle OK button click."""
        self._save_settings()
        self.EndModal(wx.ID_OK)

    def _on_reset(self, event):
        """Handle Reset to Defaults button click."""
        confirm = wx.MessageBox(
            "Are you sure you want to reset all settings to their default values?",
            "Confirm Reset",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )

        if confirm == wx.YES:
            self.settings_manager.reset_to_defaults()
            self._load_settings()
            wx.MessageBox(
                "Settings have been reset to defaults.\n\n"
                "Click OK to save, or Cancel to discard changes.",
                "Settings Reset",
                wx.OK | wx.ICON_INFORMATION,
            )

    def _on_warning_check_changed(self, event):
        """Handle warning sound checkbox change to enable/disable spin control."""
        enabled = self.play_warning_check.GetValue()
        self.warning_seconds_spin.Enable(enabled)
        self.warning_seconds_label.Enable(enabled)
