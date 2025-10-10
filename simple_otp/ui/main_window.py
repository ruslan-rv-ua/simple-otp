"""Main window for simple-otp application."""

from pathlib import Path

import wx
import wx.adv
from ObjectListView3 import ColumnDefn, Filter, ObjectListView

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.core.authenticator import Authenticator
from simple_otp.core.i18n import _
from simple_otp.core.recent_files_manager import RecentFilesManager
from simple_otp.core.settings_manager import SettingsManager
from simple_otp.core.version_utils import get_app_version
from simple_otp.models.totp_account import TOTPAccount
from simple_otp.ui.add_account_dialog import AddAccountDialog
from simple_otp.ui.constants import MAX_PATH_DISPLAY_LENGTH, SEARCH_MIN_LENGTH
from simple_otp.ui.file_controller import FileController
from simple_otp.ui.settings_dialog import SettingsDialog
from simple_otp.ui.totp_dialog import TOTPDialog


class MainWindow(wx.Frame):
    """Main application window with search and accounts list."""

    def __init__(self, parent):
        """
        Initialize the main window.

        Args:
            parent: Parent window (typically None)
        """
        super().__init__(parent, title=_("main.title"), style=wx.DEFAULT_FRAME_STYLE)

        # Store the password for decrypting accounts
        self.password = None

        # Maximize the window
        self.Maximize()

        # Initialize accounts manager (None if no file open)
        self.accounts_manager = None
        self.current_file = None

        # Initialize settings manager
        self.settings_manager = SettingsManager()

        # Initialize helper modules
        self.authenticator = Authenticator(self)
        self.recent_files_manager = RecentFilesManager(self.settings_manager)
        self.file_controller = FileController(self, self.authenticator)

        # Store reference to Recent Files submenu for dynamic updates
        self.recent_files_menu = None

        # Create the UI components
        self._create_menu_bar()
        self._create_ui()

        # Update window title with filename
        self._update_title()

        # Schedule opening the last file after the window is shown
        # This ensures the password dialog appears centered on the main window
        wx.CallAfter(self._open_last_file_on_startup)

    def _create_menu_bar(self):
        """Create the menu bar with File, Account, Tools, and Help menus."""
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        new_item = file_menu.Append(
            wx.ID_ANY, _("main.menu.file.new"), _("main.menu.file.new_hint")
        )
        open_item = file_menu.Append(
            wx.ID_ANY, _("main.menu.file.open"), _("main.menu.file.open_hint")
        )

        # Recent Files submenu
        self.recent_files_menu = wx.Menu()
        file_menu.AppendSubMenu(
            self.recent_files_menu, _("main.menu.file.recent_files")
        )

        file_menu.AppendSeparator()
        exit_item = file_menu.Append(
            wx.ID_EXIT, _("main.menu.file.exit"), _("main.menu.file.exit_hint")
        )
        menu_bar.Append(file_menu, _("main.menu.file.file"))

        # Account menu
        account_menu = wx.Menu()
        add_item = account_menu.Append(
            wx.ID_ANY,
            _("main.menu.account.add"),
            _("main.menu.account.add_hint"),
        )
        delete_item = account_menu.Append(
            wx.ID_ANY,
            _("main.menu.account.delete"),
            _("main.menu.account.delete_hint"),
        )
        menu_bar.Append(account_menu, _("main.menu.account.account"))

        # Options menu
        options_menu = wx.Menu()

        # Language submenu
        language_menu = wx.Menu()
        self._create_language_menu(language_menu)
        options_menu.AppendSubMenu(language_menu, _("main.menu.options.language"))

        options_menu.AppendSeparator()
        settings_item = options_menu.Append(
            wx.ID_ANY,
            _("main.menu.options.settings"),
            _("main.menu.options.settings_hint"),
        )
        menu_bar.Append(options_menu, _("main.menu.options.options"))

        # Help menu
        help_menu = wx.Menu()
        user_guide_item = help_menu.Append(
            wx.ID_ANY,
            _("main.menu.help.user_guide"),
            _("main.menu.help.user_guide_hint"),
        )
        help_menu.AppendSeparator()
        about_item = help_menu.Append(
            wx.ID_ABOUT,
            _("main.menu.help.about"),
            _("main.menu.help.about_hint"),
        )
        menu_bar.Append(help_menu, _("main.menu.help.help"))

        self.SetMenuBar(menu_bar)

        # Bind menu events
        self.Bind(wx.EVT_MENU, self._on_new_file, new_item)
        self.Bind(wx.EVT_MENU, self._on_open_file, open_item)
        self.Bind(wx.EVT_MENU, self._on_add_account, add_item)
        self.Bind(wx.EVT_MENU, self._on_delete_account, delete_item)
        self.Bind(wx.EVT_MENU, self._on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self._on_settings, settings_item)
        self.Bind(wx.EVT_MENU, self._on_user_guide, user_guide_item)
        self.Bind(wx.EVT_MENU, self._on_about, about_item)

        # Load recent files menu
        self._load_recent_files_menu()

    def _create_language_menu(self, menu: wx.Menu):
        """
        Create the language selection submenu.

        Args:
            menu: The menu to populate with language items
        """
        from simple_otp.core.i18n import get_available_locales, get_locale_native_name

        available_locales = get_available_locales()
        current_locale = self.settings_manager.get("locale")

        for locale_code in available_locales:
            # Get native language name from locale file
            language_name = get_locale_native_name(locale_code)

            # Create menu item
            item = menu.AppendRadioItem(wx.ID_ANY, language_name)

            # Check if this is the current locale
            if locale_code == current_locale:
                item.Check()

            # Bind event handler
            self.Bind(
                wx.EVT_MENU,
                lambda event, loc=locale_code: self._on_language_change(event, loc),
                item,
            )

    def _create_ui(self):
        """Create the main UI layout."""
        # Main panel
        panel = wx.Panel(self)

        # Create a vertical box sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Search editor at the top
        search_label = wx.StaticText(panel, label=_("main.search"))
        main_sizer.Add(search_label, 0, wx.ALL | wx.EXPAND, 5)

        self.search_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        main_sizer.Add(self.search_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        # Bind search event
        self.search_ctrl.Bind(wx.EVT_TEXT, self._on_search)

        # Accounts list (ObjectListView)
        self.accounts_list = ObjectListView(
            panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_SUNKEN
        )

        # Configure the list - single column for name
        self.accounts_list.SetColumns(
            [
                ColumnDefn(
                    title=_("main.account_column_name"),
                    valueGetter="get_display_name",
                    width=1000,
                )
            ]
        )

        # Add the list to the sizer (with proportion 1 to take remaining space)
        main_sizer.Add(self.accounts_list, 1, wx.ALL | wx.EXPAND, 5)

        # Bind list item activation event (double-click or Enter)
        self.accounts_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)

        panel.SetSizer(main_sizer)

    def _load_accounts(self):
        """Load accounts from the accounts manager."""
        if self.accounts_manager:
            accounts = self.accounts_manager.list_accounts()
            self.accounts_list.SetObjects(accounts)
            if accounts:  # Select and focus the first account if available
                self.accounts_list.Select(0)
                self.accounts_list.Focus(0)
        else:
            self.accounts_list.SetObjects([])

    def _ensure_file_open(self) -> bool:
        """
        Ensure a file is open and password is available.

        Returns:
            True if file and password are available, False otherwise
        """
        if not self.accounts_manager or not self.password:
            self._show_warning(
                _("main.messages.no_file_open"), _("main.dialogs.no_file")
            )
            return False
        return True

    # Helper methods for consistent message dialogs
    def _show_error(self, message: str, title: str | None = None):
        """
        Show error message dialog.

        Args:
            message: Error message to display
            title: Dialog title (defaults to localized "Error")
        """
        if title is None:
            title = _("main.dialogs.error")
        wx.MessageBox(message, title, wx.OK | wx.ICON_ERROR)

    def _show_warning(self, message: str, title: str | None = None):
        """
        Show warning message dialog.

        Args:
            message: Warning message to display
            title: Dialog title (defaults to localized "Warning")
        """
        if title is None:
            title = _("main.dialogs.warning")
        wx.MessageBox(message, title, wx.OK | wx.ICON_WARNING)

    def _show_success(self, message: str, title: str | None = None):
        """
        Show success/info message dialog.

        Args:
            message: Success message to display
            title: Dialog title (defaults to localized "Success")
        """
        if title is None:
            title = _("main.dialogs.success")
        wx.MessageBox(message, title, wx.OK | wx.ICON_INFORMATION)

    def _on_search(self, event):
        """Handle search text change."""
        search_text = self.search_ctrl.GetValue().strip()

        # Only filter if SEARCH_MIN_LENGTH or more characters
        if len(search_text) < SEARCH_MIN_LENGTH:
            # Clear filter if less than SEARCH_MIN_LENGTH characters
            self.accounts_list.SetFilter(None)
            self.accounts_list.RepopulateList()
            return

        # Split search text into words
        search_words = search_text.lower().split()

        # Create a filter that checks if all words are present in name or issuer
        def filter_func(account):
            # Combine name and issuer for searching
            search_target = f"{account.name} {account.issuer}".lower()

            # Check if all words are present
            return all(word in search_target for word in search_words)

        # Apply the filter
        self.accounts_list.SetFilter(Filter.Predicate(filter_func))
        self.accounts_list.RepopulateList()

    def _on_item_activated(self, event):
        """Handle list item activation (double-click or Enter)."""
        if not self._ensure_file_open():
            return

        account = self.accounts_list.GetSelectedObject()
        if account is None:
            return

        try:
            # Show TOTP dialog using the stored password and settings
            dialog = TOTPDialog(self, account, self.password, self.settings_manager)
            dialog.ShowModal()
            dialog.Destroy()
        except Exception as e:
            self._show_error(_("main.messages.failed_to_display_totp", error=str(e)))

    def _on_add_account(self, event):
        """Handle Add Account menu item."""
        if not self._ensure_file_open():
            return

        # Show the add account dialog
        dialog = AddAccountDialog(self, self.settings_manager)
        result = dialog.ShowModal()

        if result == wx.ID_OK:
            # Get the account data from the dialog
            account_data = dialog.get_account_data()

            try:
                # Create a new TOTP account with the provided data
                new_account = TOTPAccount.from_secret(
                    name=account_data["name"],
                    secret=account_data["secret"],
                    password=self.password,
                    issuer=account_data["issuer"],
                    digits=account_data["digits"],
                    digest=account_data["digest"],
                    interval=account_data["interval"],
                )

                # Add the account to the accounts manager
                self.accounts_manager.add_account(new_account)

                # Refresh the accounts list
                self._load_accounts()

                # Show success message
                self._show_success(
                    _(
                        "main.messages.account_added",
                        name=new_account.get_display_name(),
                    ),
                    _("main.dialogs.account_added"),
                )

            except ValueError as e:
                # Handle duplicate account or validation errors
                self._show_error(_("main.messages.failed_to_add_account", error=str(e)))
            except Exception as e:
                # Handle any other errors
                self._show_error(_("main.messages.unexpected_error", error=str(e)))

        dialog.Destroy()

    def _on_delete_account(self, event):
        """Handle Delete Account menu item."""
        if not self._ensure_file_open():
            return

        selected = self.accounts_list.GetSelectedObject()
        if selected is None:
            self._show_warning(
                _("main.messages.no_account_selected"),
                _("main.dialogs.confirm_delete"),
            )
            return

        # Check if this is the last account
        accounts = self.accounts_manager.list_accounts()
        is_last_account = len(accounts) == 1

        # Confirm deletion
        confirm_msg = _(
            "main.messages.delete_confirm", name=selected.get_display_name()
        )
        if is_last_account:
            confirm_msg += _("main.messages.delete_last_account")

        confirm = wx.MessageBox(
            confirm_msg,
            _("main.dialogs.confirm_delete"),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )

        if confirm != wx.YES:
            return

        # Delete the account
        try:
            if self.accounts_manager.delete_account(selected.name, selected.issuer):
                # Refresh the list
                self._load_accounts()
                self._show_success(
                    _(
                        "main.messages.account_deleted",
                        name=selected.get_display_name(),
                    ),
                    _("main.dialogs.account_deleted"),
                )
            else:
                self._show_error(_("main.messages.failed_to_delete_not_found"))
        except Exception as e:
            self._show_error(_("main.messages.failed_to_delete_account", error=str(e)))

    def _on_exit(self, event):
        """Handle Exit menu item."""
        self.Close()

    def _on_settings(self, event):
        """Handle Settings menu item."""
        dialog = SettingsDialog(self, self.settings_manager)
        dialog.ShowModal()
        dialog.Destroy()

    def _on_language_change(self, event, locale_code: str):
        """
        Handle language selection menu item.

        Args:
            event: Menu event
            locale_code: The selected locale code (e.g., "en-US", "uk-UA")
        """
        from simple_otp.core.i18n import set_locale

        # Save the new locale to settings
        self.settings_manager.set("locale", locale_code)
        self.settings_manager.save()

        # Apply the new locale
        set_locale(locale_code)

        # Show restart message
        self._show_success(
            _("main.messages.language_changed"), _("main.dialogs.language_changed")
        )

    def _on_user_guide(self, event):
        """Handle User Guide menu item - opens help documentation in browser."""
        import webbrowser

        from simple_otp.core.help_converter import HelpConverter

        # Get current locale to determine which help file to open
        locale = self.settings_manager.get("locale")

        # Construct path to Markdown help file in simple_otp/docs/
        docs_path = Path(__file__).parent.parent / "docs"
        md_file_path = docs_path / f"{locale}.md"

        # Fallback to English if locale-specific help doesn't exist
        if not md_file_path.exists():
            md_file_path = docs_path / "en-US.md"

        # Convert Markdown to HTML
        if md_file_path.exists():
            try:
                converter = HelpConverter()
                html_file_path = converter.convert_md_to_html(md_file_path)

                # Open in default browser
                file_url = html_file_path.as_uri()
                webbrowser.open(file_url)
            except Exception as e:
                self._show_error(f"Error converting help file: {e}", "Error")
        else:
            self._show_error("Help file not found.", "Error")

    def _on_about(self, event):
        """Handle About menu item."""
        # Read version from pyproject.toml
        # TODO: update the URL and developer info
        version = get_app_version()

        info = wx.adv.AboutDialogInfo()
        info.SetName(_("main.title"))
        info.SetVersion(version)
        info.SetDescription(_("about.description"))
        info.SetWebSite(_("about.website"))
        info.AddDeveloper(_("about.developer"))

        wx.adv.AboutBox(info)

    def _update_title(self):
        """Update window title to show current file name."""
        if self.current_file:
            filename = self.current_file.name
            self.SetTitle(_("main.title_with_file", filename=filename))
        else:
            self.SetTitle(_("main.title_no_file"))

    def _open_last_file_on_startup(self):
        """
        Check settings and attempt to open the last used file on startup.

        If the setting is enabled and a recent file exists, attempts to
        authenticate and open it. If authentication fails or is cancelled,
        the window remains with no file open.
        """
        # Check if we should open the last file
        if not self.settings_manager.get("files.open_last_file_on_startup", True):
            return

        # Get recent files list
        recent_files = self.recent_files_manager.get_recent_files()
        if not recent_files:
            return

        # Get the last file path
        last_file_path = recent_files[0]

        # Check if the file exists
        if not last_file_path.exists():
            # File doesn't exist anymore - remove from recent files
            self.recent_files_manager.remove_file(last_file_path)
            return

        # Authenticate against this specific file
        accounts_manager, password = self.authenticator.authenticate(last_file_path)

        if accounts_manager and password:
            # Switch to the file
            self._switch_to_file(last_file_path, accounts_manager, password)
        # If authentication was cancelled or failed, just continue with no file

    def _switch_to_file(
        self, file_path: Path, accounts_manager: AccountsManager, password: str
    ) -> bool:
        """
        Switch to a different accounts file.

        Args:
            file_path: Path to the accounts file
            accounts_manager: Pre-authenticated AccountsManager instance
            password: Password for decrypting the accounts

        Returns:
            True if successfully switched, False otherwise
        """
        # Switch to the new file
        self.accounts_manager = accounts_manager
        self.current_file = file_path
        self.password = password

        # Update window title
        self._update_title()

        # Reload accounts list
        self._load_accounts()

        # Update recent files
        self._update_recent_files(file_path)

        return True

    def _update_recent_files(self, file_path: Path):
        """
        Add file to recent files list and save settings.

        Args:
            file_path: Path to the accounts file
        """
        # Use RecentFilesManager to add file
        self.recent_files_manager.add_file(file_path)

        # Reload the recent files menu
        self._load_recent_files_menu()

    def _load_recent_files_menu(self):
        """Dynamically update the Recent Files submenu."""
        # Clear existing menu items
        for item in self.recent_files_menu.GetMenuItems():
            self.recent_files_menu.Delete(item)

        # Get recent files from RecentFilesManager
        recent_files = self.recent_files_manager.get_recent_files_strings()

        if not recent_files:
            # Show "No recent files" as disabled item
            no_files_item = self.recent_files_menu.Append(
                wx.ID_ANY, _("main.menu.file.no_recent_files")
            )
            no_files_item.Enable(False)
        else:
            # Add each recent file
            for file_path_str in recent_files:
                file_path = Path(file_path_str)

                # Format the display text (show shortened path if too long)
                display_text = self._format_file_path(file_path)

                # Create menu item
                item = self.recent_files_menu.Append(wx.ID_ANY, display_text)

                # Bind event with lambda to capture file_path
                self.Bind(
                    wx.EVT_MENU,
                    lambda evt, path=file_path: self._on_recent_file_selected(path),
                    item,
                )

            # Add separator and "Clear History"
            self.recent_files_menu.AppendSeparator()
            clear_item = self.recent_files_menu.Append(
                wx.ID_ANY, _("main.menu.file.clear_history")
            )
            self.Bind(wx.EVT_MENU, self._on_clear_recent_files, clear_item)

    def _format_file_path(self, file_path: Path) -> str:
        """
        Format a file path for display in menu (shorten if too long).

        Args:
            file_path: Path to format

        Returns:
            Formatted path string
        """
        path_str = str(file_path)

        # If path is too long, shorten it
        if len(path_str) > MAX_PATH_DISPLAY_LENGTH:
            # Get drive and filename
            parts = file_path.parts
            if len(parts) > 2:
                # Show drive + ... + filename
                return f"{parts[0]}\\...\\{file_path.name}"

        return path_str

    def _on_new_file(self, event):
        """Handle New File menu item."""
        # Use FileController to create new file
        file_path, accounts_manager, password = self.file_controller.create_new_file()

        if file_path and accounts_manager and password:
            # Switch to the new file
            self._switch_to_file(file_path, accounts_manager, password)

            self._show_success(
                _("main.messages.file_created", filename=file_path.name),
                _("main.dialogs.file_created"),
            )

    def _on_open_file(self, event):
        """Handle Open File menu item."""
        # Use FileController to open file (shows dialog and authenticates)
        file_path, accounts_manager, password = self.file_controller.open_file()

        if file_path and accounts_manager and password:
            # Switch to the file
            self._switch_to_file(file_path, accounts_manager, password)

    def _on_recent_file_selected(self, file_path: Path):
        """
        Handle Recent File selection.

        Args:
            file_path: Path to the selected file
        """
        # Use FileController to open file (handles existence check and authentication)
        result_path, accounts_manager, password = self.file_controller.open_file(
            file_path
        )

        if result_path and accounts_manager and password:
            # Switch to the file
            self._switch_to_file(result_path, accounts_manager, password)
        elif not file_path.exists():
            # File doesn't exist - remove from recent files
            self.recent_files_manager.remove_file(file_path)
            self._load_recent_files_menu()

    def _on_clear_recent_files(self, event):
        """Handle Clear History menu item."""
        confirm = wx.MessageBox(
            _("main.messages.clear_history_confirm"),
            _("main.dialogs.confirm_clear"),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )

        if confirm == wx.YES:
            self.recent_files_manager.clear_history()
            self._load_recent_files_menu()

            self._show_success(
                _("main.messages.history_cleared"),
                _("main.dialogs.history_cleared"),
            )
