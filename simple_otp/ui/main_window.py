"""Main window for simple-otp application."""

import wx
import wx.adv
from ObjectListView3 import ColumnDefn, Filter, ObjectListView

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.models.totp_account import TOTPAccount
from simple_otp.ui.add_account_dialog import AddAccountDialog
from simple_otp.ui.totp_dialog import TOTPDialog


class MainWindow(wx.Frame):
    """Main application window with search and accounts list."""

    def __init__(self, parent, password: str):
        """
        Initialize the main window.

        Args:
            parent: Parent window (typically None)
            password: Master password for decrypting accounts
        """
        super().__init__(parent, title="Simple OTP", style=wx.DEFAULT_FRAME_STYLE)

        # Store the password for decrypting accounts
        self.password = password

        # Maximize the window
        self.Maximize()

        # Initialize accounts manager
        self.accounts_manager = AccountsManager()

        # Create the UI components
        self._create_menu_bar()
        self._create_ui()

        # Load accounts from storage
        self._load_accounts()

    def _create_menu_bar(self):
        """Create the menu bar with Account and Help menus."""
        menu_bar = wx.MenuBar()

        # Account menu
        account_menu = wx.Menu()
        add_item = account_menu.Append(wx.ID_ANY, "Add\tF7", "Add new account")
        delete_item = account_menu.Append(
            wx.ID_ANY, "Delete\tDel", "Delete selected account"
        )
        account_menu.AppendSeparator()
        exit_item = account_menu.Append(wx.ID_EXIT, "E&xit\tEsc", "Exit application")
        menu_bar.Append(account_menu, "&Account")

        # Help menu
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "About Simple OTP")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        # Bind menu events
        self.Bind(wx.EVT_MENU, self._on_add_account, add_item)
        self.Bind(wx.EVT_MENU, self._on_delete_account, delete_item)
        self.Bind(wx.EVT_MENU, self._on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self._on_about, about_item)

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
        accounts = self.accounts_manager.list_accounts()
        self.accounts_list.SetObjects(accounts)

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
        account = self.accounts_list.GetSelectedObject()
        if account is None:
            return

        try:
            # Show TOTP dialog using the stored password
            dialog = TOTPDialog(self, account, self.password)
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
        # Show the add account dialog
        dialog = AddAccountDialog(self)
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
                "\n\nThis is the last account. "
                "The application will close after deletion."
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
                # If this was the last account, show message and close the app
                if is_last_account:
                    wx.MessageBox(
                        f"Account deleted: {selected.get_display_name()}\n\n"
                        "The application will now close.",
                        "Last Account Deleted",
                        wx.OK | wx.ICON_INFORMATION,
                    )
                    self.Close()
                else:
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
            from pathlib import Path

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
