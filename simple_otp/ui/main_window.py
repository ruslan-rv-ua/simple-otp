"""Main window for simple-otp application."""

import json
from pathlib import Path

import wx
import wx.adv
from ObjectListView3 import ColumnDefn, Filter, ObjectListView

from simple_otp.constants import MAX_RECENT_FILES
from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.core.settings_manager import SettingsManager
from simple_otp.models.totp_account import TOTPAccount
from simple_otp.ui.add_account_dialog import AddAccountDialog
from simple_otp.ui.password_dialog import PasswordDialog
from simple_otp.ui.settings_dialog import SettingsDialog
from simple_otp.ui.totp_dialog import TOTPDialog


class MainWindow(wx.Frame):
    """Main application window with search and accounts list."""

    def __init__(
        self,
        parent,
        password: str | None = None,
        accounts_file: Path | None = None,
    ):
        """
        Initialize the main window.

        Args:
            parent: Parent window (typically None)
            password: Master password for decrypting accounts (None if no file open)
            accounts_file: Optional path to accounts file (None if no file open)
        """
        super().__init__(parent, title="Simple OTP", style=wx.DEFAULT_FRAME_STYLE)

        # Store the password for decrypting accounts
        self.password = password

        # Maximize the window
        self.Maximize()

        # Initialize accounts manager (None if no file open)
        self.accounts_manager = None
        self.current_file = None

        if accounts_file and password:
            self.accounts_manager = AccountsManager(storage_path=accounts_file)
            self.current_file = accounts_file

        # Initialize settings manager
        self.settings_manager = SettingsManager()

        # Store reference to Recent Files submenu for dynamic updates
        self.recent_files_menu = None

        # Create the UI components
        self._create_menu_bar()
        self._create_ui()

        # Update window title with filename
        self._update_title()

        # Add current file to recent files (if we have one)
        if self.current_file:
            self._update_recent_files(self.current_file)

        # Load accounts from storage (if we have a file)
        if self.accounts_manager:
            self._load_accounts()
        else:
            # Show empty state message
            self._show_no_file_message()

    def _create_menu_bar(self):
        """Create the menu bar with File, Account, Tools, and Help menus."""
        menu_bar = wx.MenuBar()

        # File menu
        file_menu = wx.Menu()
        new_item = file_menu.Append(
            wx.ID_ANY, "&New...\tCtrl+N", "Create new accounts file"
        )
        open_item = file_menu.Append(
            wx.ID_ANY, "&Open...\tCtrl+O", "Open existing accounts file"
        )

        # Recent Files submenu
        self.recent_files_menu = wx.Menu()
        file_menu.AppendSubMenu(self.recent_files_menu, "Recent &Files")

        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tEsc", "Exit application")
        menu_bar.Append(file_menu, "&File")

        # Account menu
        account_menu = wx.Menu()
        add_item = account_menu.Append(wx.ID_ANY, "Add\tF7", "Add new account")
        delete_item = account_menu.Append(
            wx.ID_ANY, "Delete\tDel", "Delete selected account"
        )
        menu_bar.Append(account_menu, "&Account")

        # Tools menu
        tools_menu = wx.Menu()
        settings_item = tools_menu.Append(
            wx.ID_ANY, "&Settings...\tCtrl+,", "Configure application settings"
        )
        menu_bar.Append(tools_menu, "&Tools")

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About Simple OTP")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        # Bind menu events
        self.Bind(wx.EVT_MENU, self._on_new_file, new_item)
        self.Bind(wx.EVT_MENU, self._on_open_file, open_item)
        self.Bind(wx.EVT_MENU, self._on_add_account, add_item)
        self.Bind(wx.EVT_MENU, self._on_delete_account, delete_item)
        self.Bind(wx.EVT_MENU, self._on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self._on_settings, settings_item)
        self.Bind(wx.EVT_MENU, self._on_about, about_item)

        # Load recent files menu
        self._load_recent_files_menu()

    def _create_ui(self):
        """Create the main UI layout."""
        # Main panel
        panel = wx.Panel(self)

        # Create a vertical box sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Search editor at the top
        search_label = wx.StaticText(panel, label="Search:")
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
                    title="Name",
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
        else:
            self.accounts_list.SetObjects([])

    def _on_search(self, event):
        """Handle search text change."""
        search_text = self.search_ctrl.GetValue().strip()

        # Only filter if 3 or more characters
        if len(search_text) < 3:
            # Clear filter if less than 3 characters
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
        if not self.accounts_manager or not self.password:
            wx.MessageBox(
                "No accounts file is open.",
                "No File",
                wx.OK | wx.ICON_WARNING,
            )
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
            wx.MessageBox(
                f"Failed to display TOTP: {str(e)}",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )

    def _on_add_account(self, event):
        """Handle Add Account menu item."""
        if not self.accounts_manager or not self.password:
            wx.MessageBox(
                "No accounts file is open.\n\nPlease create or open a file first.",
                "No File",
                wx.OK | wx.ICON_WARNING,
            )
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
                wx.MessageBox(
                    f"Account added successfully: {new_account.get_display_name()}",
                    "Account Added",
                    wx.OK | wx.ICON_INFORMATION,
                )

            except ValueError as e:
                # Handle duplicate account or validation errors
                wx.MessageBox(
                    f"Failed to add account: {str(e)}",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )
            except Exception as e:
                # Handle any other errors
                wx.MessageBox(
                    f"An unexpected error occurred: {str(e)}",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )

        dialog.Destroy()

    def _on_delete_account(self, event):
        """Handle Delete Account menu item."""
        if not self.accounts_manager:
            wx.MessageBox(
                "No accounts file is open.",
                "No File",
                wx.OK | wx.ICON_WARNING,
            )
            return

        selected = self.accounts_list.GetSelectedObject()
        if selected is None:
            wx.MessageBox(
                "No account selected", "Delete Account", wx.OK | wx.ICON_WARNING
            )
            return

        # Check if this is the last account
        accounts = self.accounts_manager.list_accounts()
        is_last_account = len(accounts) == 1

        # Confirm deletion
        confirm_msg = f"Are you sure you want to delete {selected.get_display_name()}?"
        if is_last_account:
            confirm_msg += (
                "\n\nThis is the last account. The file will remain open but empty."
            )

        confirm = wx.MessageBox(
            confirm_msg,
            "Confirm Delete",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )

        if confirm != wx.YES:
            return

        # Delete the account
        try:
            if self.accounts_manager.delete_account(selected.name, selected.issuer):
                # Refresh the list
                self._load_accounts()
                wx.MessageBox(
                    f"Account deleted: {selected.get_display_name()}",
                    "Account Deleted",
                    wx.OK | wx.ICON_INFORMATION,
                )
            else:
                wx.MessageBox(
                    "Failed to delete account (not found)",
                    "Error",
                    wx.OK | wx.ICON_ERROR,
                )
        except Exception as e:
            wx.MessageBox(
                f"Failed to delete account: {str(e)}",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )

    def _on_exit(self, event):
        """Handle Exit menu item."""
        self.Close()

    def _on_settings(self, event):
        """Handle Settings menu item."""
        dialog = SettingsDialog(self, self.settings_manager)
        dialog.ShowModal()
        dialog.Destroy()

    def _on_about(self, event):
        """Handle About menu item."""
        # Read version from pyproject.toml
        # TODO: update the URL and developer info
        version = self._get_app_version()

        info = wx.adv.AboutDialogInfo()
        info.SetName("Simple OTP")
        info.SetVersion(version)
        info.SetDescription("Desktop application for generating TOTP codes")
        info.SetWebSite("https://github.com/yourusername/simple-otp")
        info.AddDeveloper("Ruslan Iskov")

        wx.adv.AboutBox(info)

    def _get_app_version(self):
        """Get the application version from pyproject.toml."""
        try:
            import tomllib

            # Get the path to pyproject.toml
            project_root = Path(__file__).parent.parent.parent
            pyproject_path = project_root / "pyproject.toml"

            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    return data.get("project", {}).get("version", "Unknown")
        except Exception:
            pass

        return "Unknown"

    def _update_title(self):
        """Update window title to show current file name."""
        if self.current_file:
            filename = self.current_file.name
            self.SetTitle(f"Simple OTP - {filename}")
        else:
            self.SetTitle("Simple OTP - No file opened")

    def _show_no_file_message(self):
        """Show message when no file is opened."""
        # Clear the accounts list
        self.accounts_list.SetObjects([])

        # Show informational message
        wx.CallAfter(
            wx.MessageBox,
            "No accounts file is currently open.\n\n"
            "Please create a new file (File > New) or\n"
            "open an existing one (File > Open).",
            "No File Opened",
            wx.OK | wx.ICON_INFORMATION,
        )

    def _switch_to_file(self, file_path: Path, password: str) -> bool:
        """
        Switch to a different accounts file.

        Args:
            file_path: Path to the accounts file
            password: Password for decrypting the accounts

        Returns:
            True if successfully switched, False otherwise
        """
        try:
            # Create a new accounts manager with the specified file
            new_manager = AccountsManager(storage_path=file_path, auto_create=False)

            # Verify the password by trying to load accounts
            if not new_manager.verify_password(password):
                wx.MessageBox(
                    "Incorrect password for this file.",
                    "Authentication Failed",
                    wx.OK | wx.ICON_ERROR,
                )
                return False

            # Switch to the new file
            self.accounts_manager = new_manager
            self.current_file = file_path
            self.password = password

            # Update window title
            self._update_title()

            # Reload accounts list
            self._load_accounts()

            # Update recent files
            self._update_recent_files(file_path)

            return True

        except FileNotFoundError:
            wx.MessageBox(
                f"File not found: {file_path}",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )
            return False
        except Exception as e:
            wx.MessageBox(
                f"Failed to open file: {str(e)}",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )
            return False

    def _update_recent_files(self, file_path: Path):
        """
        Add file to recent files list and save settings.

        Args:
            file_path: Path to the accounts file
        """
        # Get current recent files list
        recent_files = self.settings_manager.get("files.recent_files", [])

        # Convert to string for comparison
        file_str = str(file_path.resolve())

        # Remove if already exists (to move to front)
        if file_str in recent_files:
            recent_files.remove(file_str)

        # Add to front
        recent_files.insert(0, file_str)

        # Keep only MAX_RECENT_FILES entries
        recent_files = recent_files[:MAX_RECENT_FILES]

        # Save to settings
        self.settings_manager.set("files.recent_files", recent_files)
        self.settings_manager.save()

        # Reload the recent files menu
        self._load_recent_files_menu()

    def _load_recent_files_menu(self):
        """Dynamically update the Recent Files submenu."""
        # Clear existing menu items
        for item in self.recent_files_menu.GetMenuItems():
            self.recent_files_menu.Delete(item)

        # Get recent files from settings
        recent_files = self.settings_manager.get("files.recent_files", [])

        if not recent_files:
            # Show "No recent files" as disabled item
            no_files_item = self.recent_files_menu.Append(wx.ID_ANY, "No recent files")
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
            clear_item = self.recent_files_menu.Append(wx.ID_ANY, "Clear History")
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
        max_length = 60
        if len(path_str) > max_length:
            # Get drive and filename
            parts = file_path.parts
            if len(parts) > 2:
                # Show drive + ... + filename
                return f"{parts[0]}\\...\\{file_path.name}"

        return path_str

    def _on_new_file(self, event):
        """Handle New File menu item."""
        # Show file dialog
        with wx.FileDialog(
            self,
            "Create New Accounts File",
            wildcard="JSON files (*.json)|*.json",
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
        ) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            file_path = Path(file_dialog.GetPath())

            # Ensure .json extension
            if file_path.suffix.lower() != ".json":
                file_path = file_path.with_suffix(".json")

        # Ask for password with confirmation
        password_dialog = PasswordDialog(
            self,
            title="Set Password",
            message="Enter a password to encrypt the new accounts file:",
            require_confirmation=True,
        )

        if password_dialog.ShowModal() != wx.ID_OK:
            password_dialog.Destroy()
            return

        new_password = password_dialog.GetPassword()
        password_dialog.Destroy()

        try:
            # Create an empty accounts file
            data = {"accounts": []}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Create new accounts manager with the file (auto_create=False)
            new_manager = AccountsManager(storage_path=file_path, auto_create=False)

            # Switch to the new file
            self.accounts_manager = new_manager
            self.current_file = file_path
            self.password = new_password

            # Update window title
            self._update_title()

            # Clear the accounts list (empty file)
            self.accounts_list.SetObjects([])

            # Update recent files
            self._update_recent_files(file_path)

            wx.MessageBox(
                f"New accounts file created: {file_path.name}\n\n"
                "You can now add your accounts.",
                "File Created",
                wx.OK | wx.ICON_INFORMATION,
            )

        except Exception as e:
            wx.MessageBox(
                f"Failed to create file: {str(e)}",
                "Error",
                wx.OK | wx.ICON_ERROR,
            )

    def _on_open_file(self, event):
        """Handle Open File menu item."""
        # Show file dialog
        with wx.FileDialog(
            self,
            "Open Accounts File",
            wildcard="JSON files (*.json)|*.json",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
        ) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return

            file_path = Path(file_dialog.GetPath())

        # Ask for password (without confirmation)
        password_dialog = PasswordDialog(
            self,
            title="Enter Password",
            message=f"Enter password for {file_path.name}:",
            require_confirmation=False,
        )

        if password_dialog.ShowModal() != wx.ID_OK:
            password_dialog.Destroy()
            return

        password = password_dialog.GetPassword()
        password_dialog.Destroy()

        # Try to switch to the file
        self._switch_to_file(file_path, password)

    def _on_recent_file_selected(self, file_path: Path):
        """
        Handle Recent File selection.

        Args:
            file_path: Path to the selected file
        """
        # Check if file exists
        if not file_path.exists():
            wx.MessageBox(
                f"File not found: {file_path}\n\n"
                "The file will be removed from recent files.",
                "File Not Found",
                wx.OK | wx.ICON_WARNING,
            )

            # Remove from recent files
            recent_files = self.settings_manager.get("files.recent_files", [])
            file_str = str(file_path.resolve())
            if file_str in recent_files:
                recent_files.remove(file_str)
                self.settings_manager.set("files.recent_files", recent_files)
                self.settings_manager.save()
                self._load_recent_files_menu()

            return

        # Ask for password
        password_dialog = PasswordDialog(
            self,
            title="Enter Password",
            message=f"Enter password for {file_path.name}:",
            require_confirmation=False,
        )

        if password_dialog.ShowModal() != wx.ID_OK:
            password_dialog.Destroy()
            return

        password = password_dialog.GetPassword()
        password_dialog.Destroy()

        # Try to switch to the file
        self._switch_to_file(file_path, password)

    def _on_clear_recent_files(self, event):
        """Handle Clear History menu item."""
        confirm = wx.MessageBox(
            "Are you sure you want to clear the recent files history?",
            "Confirm Clear",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION,
        )

        if confirm == wx.YES:
            self.settings_manager.set("files.recent_files", [])
            self.settings_manager.save()
            self._load_recent_files_menu()

            wx.MessageBox(
                "Recent files history cleared.",
                "History Cleared",
                wx.OK | wx.ICON_INFORMATION,
            )
