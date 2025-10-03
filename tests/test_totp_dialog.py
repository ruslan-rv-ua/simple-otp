"""Tests for TOTP Dialog."""

import tempfile
from pathlib import Path

import pytest
import wx

from simple_otp.core.settings_manager import SettingsManager
from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount
from simple_otp.ui.totp_dialog import TOTPDialog, format_otp


class TestTOTPDialog:
    """Tests for TOTPDialog."""

    @pytest.fixture
    def app(self):
        """Create a wxPython app for testing."""
        app = wx.App()
        yield app
        app.Destroy()

    @pytest.fixture
    def temp_settings_file(self):
        """Create a temporary settings file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = Path(f.name)
        if temp_file.exists():
            temp_file.unlink()
        yield temp_file
        if temp_file.exists():
            temp_file.unlink()

    @pytest.fixture
    def settings_manager(self, temp_settings_file):
        """Create a SettingsManager with a temporary file."""
        return SettingsManager(temp_settings_file)

    @pytest.fixture
    def account(self):
        """Create a test TOTP account."""
        return TOTPAccount.from_secret(
            name="test@example.com",
            secret="JBSWY3DPEHPK3PXP",
            password="demo123",
            issuer="Test Service",
            digits=6,
            digest=DigestAlgorithm.SHA1,
            interval=30,
        )

    @pytest.fixture
    def dialog(self, app, account, settings_manager):
        """Create a TOTPDialog instance."""
        dialog = TOTPDialog(None, account, "demo123", settings_manager)
        yield dialog
        dialog.Destroy()

    def test_format_otp(self):
        """Test OTP formatting function."""
        # Test 6-digit code
        assert format_otp("123456") == "12 34 56"

        # Test 8-digit code
        assert format_otp("12345678") == "12 34 56 78"

    def test_dialog_creation(self, dialog, account):
        """Test that dialog is created successfully."""
        assert dialog is not None
        assert dialog.GetTitle() == f"TOTP - {account.get_display_name()}"
        assert dialog.account == account
        assert dialog.password == "demo123"

    def test_update_codes_and_progress(self, dialog):
        """Test that codes and progress are updated correctly."""
        # Call the update method
        dialog._update_codes_and_progress()

        # Check that current and next codes are set (should be non-empty strings)
        current_code = dialog.current_text.GetValue()
        next_code = dialog.next_text.GetValue()

        assert len(current_code) > 0
        assert len(next_code) > 0

        # With default hide_passwords=True, codes should be "******"
        if dialog.hide_passwords:
            assert current_code == "******"
            assert next_code == "******"
        else:
            # Check that codes are formatted with spaces
            assert " " in current_code
            assert " " in next_code

        # Check that progress bar has a value between 0 and 100
        progress = dialog.progress_bar.GetValue()
        assert 0 <= progress <= 100

    def test_copy_current_button(self, dialog, monkeypatch):
        """Test copying current OTP to clipboard."""
        import pyperclip

        # Mock pyperclip.copy to verify it's called
        copied_text = []
        original_copy = pyperclip.copy

        def mock_copy(text):
            copied_text.append(text)
            return original_copy(text)

        monkeypatch.setattr(pyperclip, "copy", mock_copy)

        # Simulate button click
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, dialog.current_copy_btn.GetId())
        dialog._on_copy_current(event)

        # Verify that a code was copied
        assert len(copied_text) == 1
        # Verify it's a valid OTP code (6-8 digits)
        assert copied_text[0].isdigit()
        assert 6 <= len(copied_text[0]) <= 8

    def test_copy_next_button(self, dialog, monkeypatch):
        """Test copying next OTP to clipboard."""
        import pyperclip

        # Mock pyperclip.copy to verify it's called
        copied_text = []
        original_copy = pyperclip.copy

        def mock_copy(text):
            copied_text.append(text)
            return original_copy(text)

        monkeypatch.setattr(pyperclip, "copy", mock_copy)

        # Simulate button click
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, dialog.next_copy_btn.GetId())
        dialog._on_copy_next(event)

        # Verify that a code was copied
        assert len(copied_text) == 1
        # Verify it's a valid OTP code (6-8 digits)
        assert copied_text[0].isdigit()
        assert 6 <= len(copied_text[0]) <= 8

    def test_audio_settings_respected_on_copy(
        self, app, account, settings_manager, monkeypatch
    ):
        """Test that audio settings are respected when copying."""
        # Disable current password copied sound
        settings_manager.set("audio.play_current_copied_sound", False)

        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock audio player to verify it's NOT called
        play_calls = []

        if dialog.audio_player:
            original_play = dialog.audio_player.play

            def mock_play(filename):
                play_calls.append(filename)
                return original_play(filename)

            monkeypatch.setattr(dialog.audio_player, "play", mock_play)

        # Simulate button click
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, dialog.current_copy_btn.GetId())
        dialog._on_copy_current(event)

        # Verify that play was NOT called (sound is disabled)
        assert len(play_calls) == 0

        dialog.Destroy()

    def test_warning_sound_threshold_respected(
        self, app, account, settings_manager, monkeypatch
    ):
        """Test that warning sound threshold setting is respected."""
        # Set warning threshold to 10 seconds
        settings_manager.set("audio.warning_sound_seconds", 10)

        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Verify that the threshold is read correctly
        warning_seconds = dialog.settings_manager.get("audio.warning_sound_seconds", 5)
        assert warning_seconds == 10

        dialog.Destroy()

    def test_auto_copy_on_update_disabled_by_default(
        self, app, account, settings_manager
    ):
        """Test that auto-copy on update is disabled by default."""
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Verify setting is False by default
        auto_copy_enabled = dialog.settings_manager.get(
            "behavior.auto_copy_on_update", False
        )
        assert auto_copy_enabled is False

        dialog.Destroy()

    def test_hide_passwords_enabled_by_default(self, app, account, settings_manager):
        """Test that hide_passwords is enabled by default."""
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Verify setting is True by default
        assert dialog.hide_passwords is True
        assert dialog.settings_manager.get("behavior.hide_passwords", True) is True

        dialog.Destroy()

    def test_passwords_hidden_when_enabled(self, app, account, settings_manager):
        """Test that OTP codes are hidden when hide_passwords is True."""
        settings_manager.set("behavior.hide_passwords", True)
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Update codes
        dialog._update_codes_and_progress()

        # Verify codes are hidden
        assert dialog.current_text.GetValue() == "******"
        assert dialog.next_text.GetValue() == "******"

        dialog.Destroy()

    def test_passwords_visible_when_disabled(self, app, account, settings_manager):
        """Test that OTP codes are visible when hide_passwords is False."""
        settings_manager.set("behavior.hide_passwords", False)
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Update codes
        dialog._update_codes_and_progress()

        # Verify codes are visible and formatted
        current_code = dialog.current_text.GetValue()
        next_code = dialog.next_text.GetValue()

        assert current_code != "******"
        assert next_code != "******"
        assert " " in current_code  # Should be formatted with spaces
        assert " " in next_code

        dialog.Destroy()

    def test_keyboard_focus_disabled_when_passwords_hidden(
        self, app, account, settings_manager
    ):
        """Test that text controls can't accept keyboard focus when hidden."""
        settings_manager.set("behavior.hide_passwords", True)
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Verify AcceptsFocusFromKeyboard is NOT set (should use default behavior)
        # When hide_passwords=True, we don't override AcceptsFocusFromKeyboard
        # so it should return the default False for read-only controls
        assert (
            not hasattr(dialog.current_text.AcceptsFocusFromKeyboard, "__self__")
            or not dialog.current_text.AcceptsFocusFromKeyboard()
        )

        dialog.Destroy()

    def test_keyboard_focus_enabled_when_passwords_visible(
        self, app, account, settings_manager
    ):
        """Test that text controls accept keyboard focus when passwords are visible."""
        settings_manager.set("behavior.hide_passwords", False)
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Verify AcceptsFocusFromKeyboard is set to True
        assert dialog.current_text.AcceptsFocusFromKeyboard()
        assert dialog.next_text.AcceptsFocusFromKeyboard()

        dialog.Destroy()

    def test_copy_works_with_hidden_passwords(
        self, app, account, settings_manager, monkeypatch
    ):
        """Test that copying OTP works even when passwords are hidden."""
        import pyperclip

        settings_manager.set("behavior.hide_passwords", True)
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock pyperclip.copy to verify correct code is copied
        copied_text = []
        original_copy = pyperclip.copy

        def mock_copy(text):
            copied_text.append(text)
            return original_copy(text)

        monkeypatch.setattr(pyperclip, "copy", mock_copy)

        # Verify display shows hidden text
        dialog._update_codes_and_progress()
        assert dialog.current_text.GetValue() == "******"

        # Copy current OTP
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, dialog.current_copy_btn.GetId())
        dialog._on_copy_current(event)

        # Verify that actual OTP code was copied, not "******"
        assert len(copied_text) == 1
        assert copied_text[0] != "******"
        assert copied_text[0].isdigit()
        assert len(copied_text[0]) == 6  # Default is 6 digits

        dialog.Destroy()

    def test_vocabraille_initialization(self, app, account, settings_manager):
        """Test that VocaBraille is initialized correctly."""
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # VocaBraille should be initialized (or None if it fails)
        assert hasattr(dialog, "vocabraille")

        dialog.Destroy()

    def test_speak_otp_method(self, app, account, settings_manager, monkeypatch):
        """Test that _speak_otp method works correctly."""
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock VocaBraille say method if it exists
        if dialog.vocabraille:
            say_calls = []

            def mock_say(msg, interrupt=True):
                say_calls.append({"msg": msg, "interrupt": interrupt})

            monkeypatch.setattr(dialog.vocabraille, "say", mock_say)

            # Test speaking OTP
            dialog._speak_otp("123456")

            # Verify say was called with correct parameters
            assert len(say_calls) == 1
            assert say_calls[0]["msg"] == "12 34 56"  # Formatted as displayed
            assert say_calls[0]["interrupt"] is True  # Should always interrupt

        dialog.Destroy()

    def test_pronounce_current_otp(self, app, account, settings_manager, monkeypatch):
        """Test pronouncing current OTP."""
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock _speak_otp to verify it's called
        speak_calls = []

        def mock_speak_otp(otp_code):
            speak_calls.append(otp_code)

        monkeypatch.setattr(dialog, "_speak_otp", mock_speak_otp)

        # Simulate keyboard shortcut or button press
        event = wx.MenuEvent(wx.wxEVT_MENU, dialog.ID_PRONOUNCE_CURRENT)
        dialog._on_pronounce_current(event)

        # Verify _speak_otp was called with current OTP
        assert len(speak_calls) == 1
        assert speak_calls[0].isdigit()
        assert len(speak_calls[0]) == 6

        dialog.Destroy()

    def test_pronounce_next_otp(self, app, account, settings_manager, monkeypatch):
        """Test pronouncing next OTP."""
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock _speak_otp to verify it's called
        speak_calls = []

        def mock_speak_otp(otp_code):
            speak_calls.append(otp_code)

        monkeypatch.setattr(dialog, "_speak_otp", mock_speak_otp)

        # Simulate keyboard shortcut or button press
        event = wx.MenuEvent(wx.wxEVT_MENU, dialog.ID_PRONOUNCE_NEXT)
        dialog._on_pronounce_next(event)

        # Verify _speak_otp was called with next OTP
        assert len(speak_calls) == 1
        assert speak_calls[0].isdigit()
        assert len(speak_calls[0]) == 6

        dialog.Destroy()

    def test_auto_speak_password_disabled_by_default(
        self, app, account, settings_manager
    ):
        """Test that auto-speak password is disabled by default."""
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Verify setting is False by default
        auto_speak_enabled = dialog.settings_manager.get(
            "behavior.auto_speak_password", False
        )
        assert auto_speak_enabled is False

        dialog.Destroy()

    def test_auto_speak_on_password_update(
        self, app, account, settings_manager, monkeypatch
    ):
        """Test that OTP is automatically spoken when it updates."""
        settings_manager.set("behavior.auto_speak_password", True)
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock _speak_otp to verify it's called
        speak_calls = []

        def mock_speak_otp(otp_code):
            speak_calls.append(otp_code)

        monkeypatch.setattr(dialog, "_speak_otp", mock_speak_otp)

        # Reset last_copied_otp to force a new update
        dialog.last_copied_otp = None

        # Trigger update
        dialog._update_codes_and_progress()

        # Verify _speak_otp was called
        assert len(speak_calls) == 1
        assert speak_calls[0].isdigit()

        dialog.Destroy()

    def test_auto_copy_and_auto_speak_work_together(
        self, app, account, settings_manager, monkeypatch
    ):
        """Test that auto-copy and auto-speak both work when enabled together."""
        import pyperclip

        # Enable both features
        settings_manager.set("behavior.auto_copy_on_update", True)
        settings_manager.set("behavior.auto_speak_password", True)
        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock pyperclip.copy to verify it's called
        copied_text = []
        original_copy = pyperclip.copy

        def mock_copy(text):
            copied_text.append(text)
            return original_copy(text)

        monkeypatch.setattr(pyperclip, "copy", mock_copy)

        # Mock _speak_otp to verify it's called
        speak_calls = []

        def mock_speak_otp(otp_code):
            speak_calls.append(otp_code)

        monkeypatch.setattr(dialog, "_speak_otp", mock_speak_otp)

        # Reset last_copied_otp to force a new update
        dialog.last_copied_otp = None

        # Trigger update
        dialog._update_codes_and_progress()

        # Verify both pyperclip.copy and _speak_otp were called
        assert len(copied_text) == 1
        assert len(speak_calls) == 1
        # Both should have the same OTP code
        assert copied_text[0] == speak_calls[0]
        assert copied_text[0].isdigit()

        dialog.Destroy()

    def test_auto_copy_plays_sound_when_enabled(
        self, app, account, settings_manager, monkeypatch
    ):
        """Test that sound is played during auto-copy when the setting is enabled."""
        import pyperclip

        # Enable auto-copy and ensure sound is enabled
        settings_manager.set("behavior.auto_copy_on_update", True)
        settings_manager.set("audio.play_current_copied_sound", True)
        settings_manager.set("audio.play_password_updated_sound", True)

        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock _play_sound_safe to track if it's called
        sound_calls = []

        def mock_play_sound_safe(filename):
            sound_calls.append(filename)

        monkeypatch.setattr(dialog, "_play_sound_safe", mock_play_sound_safe)

        # Mock pyperclip.copy
        copied_text = []
        original_copy = pyperclip.copy

        def mock_copy(text):
            copied_text.append(text)
            return original_copy(text)

        monkeypatch.setattr(pyperclip, "copy", mock_copy)

        # Reset last_copied_otp to force a new update
        dialog.last_copied_otp = None

        # Trigger update
        dialog._update_codes_and_progress()

        # Verify that pyperclip.copy was called
        assert len(copied_text) == 1
        # Verify that _play_sound_safe was called with both sound files
        # (current_password_copied.wav and password_updated.wav)
        assert len(sound_calls) == 2
        assert "current_password_copied.wav" in sound_calls
        assert "password_updated.wav" in sound_calls

        dialog.Destroy()

    def test_auto_copy_does_not_play_sound_when_disabled(
        self, app, account, settings_manager, monkeypatch
    ):
        """Test that sound is NOT played during auto-copy when disabled."""
        import pyperclip

        # Enable auto-copy but disable sounds
        settings_manager.set("behavior.auto_copy_on_update", True)
        settings_manager.set("audio.play_current_copied_sound", False)
        settings_manager.set("audio.play_password_updated_sound", False)

        dialog = TOTPDialog(None, account, "demo123", settings_manager)

        # Mock _play_sound_safe to track if it's called
        sound_calls = []

        def mock_play_sound_safe(filename):
            sound_calls.append(filename)

        monkeypatch.setattr(dialog, "_play_sound_safe", mock_play_sound_safe)

        # Mock pyperclip.copy
        copied_text = []
        original_copy = pyperclip.copy

        def mock_copy(text):
            copied_text.append(text)
            return original_copy(text)

        monkeypatch.setattr(pyperclip, "copy", mock_copy)

        # Reset last_copied_otp to force a new update
        dialog.last_copied_otp = None

        # Trigger update
        dialog._update_codes_and_progress()

        # Verify that pyperclip.copy was called
        assert len(copied_text) == 1
        # Verify that _play_sound_safe was NOT called
        assert len(sound_calls) == 0

        dialog.Destroy()


if __name__ == "__main__":
    pytest.main([__file__])
