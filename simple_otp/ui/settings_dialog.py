"""Settings dialog for simple-otp application."""

import wx

from simple_otp.core.i18n import _
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
            title=_("settings.title"),
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
        self._create_behavior_page()
        self._create_audio_page()
        self._create_totp_page()

        main_sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 10)

        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.reset_button = wx.Button(panel, label=_("settings.button_reset"))
        self.reset_button.Bind(wx.EVT_BUTTON, self._on_reset)
        button_sizer.Add(self.reset_button, 0, wx.ALL, 5)

        button_sizer.AddStretchSpacer()

        ok_button = wx.Button(panel, wx.ID_OK, _("settings.button_ok"))
        ok_button.Bind(wx.EVT_BUTTON, self._on_ok)
        button_sizer.Add(ok_button, 0, wx.ALL, 5)

        cancel_button = wx.Button(panel, wx.ID_CANCEL, _("settings.button_cancel"))
        button_sizer.Add(cancel_button, 0, wx.ALL, 5)

        main_sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(main_sizer)

    def _create_totp_page(self):
        """Create the TOTP settings page."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Default digits
        digits_label = wx.StaticText(panel, label=_("settings.totp.default_digits"))
        sizer.Add(digits_label, 0, wx.ALL, 5)

        self.digits_choice = wx.Choice(panel, choices=["6", "7", "8"])
        self.digits_choice.SetSelection(0)
        sizer.Add(self.digits_choice, 0, wx.ALL | wx.EXPAND, 5)

        # Default interval
        interval_label = wx.StaticText(panel, label=_("settings.totp.default_interval"))
        sizer.Add(interval_label, 0, wx.ALL, 5)

        self.interval_spin = wx.SpinCtrl(panel, value="30", min=15, max=120)
        sizer.Add(self.interval_spin, 0, wx.ALL | wx.EXPAND, 5)

        # Default digest
        digest_label = wx.StaticText(panel, label=_("settings.totp.default_digest"))
        sizer.Add(digest_label, 0, wx.ALL, 5)

        self.digest_choice = wx.Choice(panel, choices=["SHA1", "SHA256", "SHA512"])
        self.digest_choice.SetSelection(0)
        sizer.Add(self.digest_choice, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, _("settings.tab_totp"))

    def _create_behavior_page(self):
        """Create the behavior settings page."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Auto-copy on update checkbox
        self.auto_copy_on_update_check = wx.CheckBox(
            panel,
            label=_("settings.behavior.auto_copy"),
        )
        sizer.Add(self.auto_copy_on_update_check, 0, wx.ALL, 5)

        # Add help text
        help_text = wx.StaticText(
            panel,
            label=_("settings.behavior.auto_copy_help"),
        )
        help_text.SetForegroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        )
        font = help_text.GetFont()
        font.PointSize = 9
        help_text.SetFont(font)
        sizer.Add(help_text, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Add spacer
        sizer.AddSpacer(10)

        # Hide passwords checkbox
        self.hide_passwords_check = wx.CheckBox(
            panel,
            label=_("settings.behavior.hide_passwords"),
        )
        sizer.Add(self.hide_passwords_check, 0, wx.ALL, 5)

        # Add help text for hide passwords
        help_text_hide = wx.StaticText(
            panel,
            label=_("settings.behavior.hide_passwords_help"),
        )
        help_text_hide.SetForegroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        )
        font_hide = help_text_hide.GetFont()
        font_hide.PointSize = 9
        help_text_hide.SetFont(font_hide)
        sizer.Add(help_text_hide, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Add spacer
        sizer.AddSpacer(10)

        # Auto-speak password checkbox
        self.auto_speak_password_check = wx.CheckBox(
            panel,
            label=_("settings.behavior.auto_speak_password"),
        )
        sizer.Add(self.auto_speak_password_check, 0, wx.ALL, 5)

        # Add help text for auto-speak password
        help_text_speak = wx.StaticText(
            panel,
            label=_("settings.behavior.auto_speak_password_help"),
        )
        help_text_speak.SetForegroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        )
        font_speak = help_text_speak.GetFont()
        font_speak.PointSize = 9
        help_text_speak.SetFont(font_speak)
        sizer.Add(help_text_speak, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        # Add spacer
        sizer.AddSpacer(10)

        # Open last file on startup checkbox
        self.open_last_file_check = wx.CheckBox(
            panel,
            label=_("settings.behavior.open_last_file"),
        )
        sizer.Add(self.open_last_file_check, 0, wx.ALL, 5)

        # Add help text for open last file
        help_text2 = wx.StaticText(
            panel,
            label=_("settings.behavior.open_last_file_help"),
        )
        help_text2.SetForegroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT)
        )
        font2 = help_text2.GetFont()
        font2.PointSize = 9
        help_text2.SetFont(font2)
        sizer.Add(help_text2, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        panel.SetSizer(sizer)
        self.notebook.AddPage(panel, _("settings.tab_behavior"))

    def _create_audio_page(self):
        """Create the audio settings page."""
        panel = wx.Panel(self.notebook)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Play password copied sound checkbox
        self.play_password_copied_check = wx.CheckBox(
            panel, label=_("settings.audio.play_password_copied")
        )
        sizer.Add(self.play_password_copied_check, 0, wx.ALL, 5)

        # Play warning sound checkbox
        self.play_warning_check = wx.CheckBox(
            panel, label=_("settings.audio.play_warning")
        )
        sizer.Add(self.play_warning_check, 0, wx.ALL, 5)

        # Warning sound seconds - label and spinctrl in horizontal layout
        warning_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.warning_seconds_label = wx.StaticText(
            panel, label=_("settings.audio.warning_seconds")
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
        self.notebook.AddPage(panel, _("settings.tab_audio"))

    def _load_settings(self):
        """Load settings from the settings manager into the UI controls."""
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

        # Behavior settings
        auto_copy_on_update = self.settings_manager.get(
            "behavior.auto_copy_on_update", False
        )
        self.auto_copy_on_update_check.SetValue(auto_copy_on_update)

        hide_passwords = self.settings_manager.get("behavior.hide_passwords", True)
        self.hide_passwords_check.SetValue(hide_passwords)

        auto_speak_password = self.settings_manager.get(
            "behavior.auto_speak_password", False
        )
        self.auto_speak_password_check.SetValue(auto_speak_password)

        open_last_file = self.settings_manager.get(
            "files.open_last_file_on_startup", True
        )
        self.open_last_file_check.SetValue(open_last_file)

    def _save_settings(self):
        """Save settings from UI controls to the settings manager."""
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

        # Behavior settings
        auto_copy_on_update = self.auto_copy_on_update_check.GetValue()
        self.settings_manager.set("behavior.auto_copy_on_update", auto_copy_on_update)

        hide_passwords = self.hide_passwords_check.GetValue()
        self.settings_manager.set("behavior.hide_passwords", hide_passwords)

        auto_speak_password = self.auto_speak_password_check.GetValue()
        self.settings_manager.set("behavior.auto_speak_password", auto_speak_password)

        open_last_file = self.open_last_file_check.GetValue()
        self.settings_manager.set("files.open_last_file_on_startup", open_last_file)

        # Save to file
        self.settings_manager.save()

    def _on_ok(self, event):
        """Handle OK button click."""
        self._save_settings()
        self.EndModal(wx.ID_OK)

    def _on_reset(self, event):
        """Handle Reset to Defaults button click."""
        confirm = wx.MessageBox(
            _("settings.messages.reset_confirm"),
            _("settings.messages.confirm_reset"),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )

        if confirm == wx.YES:
            self.settings_manager.reset_to_defaults()
            self._load_settings()
            wx.MessageBox(
                _("settings.messages.reset_success"),
                _("settings.messages.settings_reset"),
                wx.OK | wx.ICON_INFORMATION,
            )

    def _on_warning_check_changed(self, event):
        """Handle warning sound checkbox change to enable/disable spin control."""
        enabled = self.play_warning_check.GetValue()
        self.warning_seconds_spin.Enable(enabled)
        self.warning_seconds_label.Enable(enabled)
