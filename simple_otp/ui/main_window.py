"""Main window for simple-otp application."""

import wx
from ObjectListView3 import ColumnDefn, Filter, ObjectListView

from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount


class MainWindow(wx.Frame):
    """Main application window with search and accounts list."""

    def __init__(self, parent):
        """Initialize the main window."""
        super().__init__(parent, title="Simple OTP", style=wx.DEFAULT_FRAME_STYLE)

        # Maximize the window
        self.Maximize()

        # Create the UI components
        self._create_menu_bar()
        self._create_ui()

        # Sample data for testing
        self._load_sample_accounts()

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

        panel.SetSizer(main_sizer)

    def _load_sample_accounts(self):
        """Load sample accounts for testing."""
        # Common password for all demo accounts
        demo_password = "demo123"

        # Standard test secret from RFC 6238
        demo_secret = "JBSWY3DPEHPK3PXP"

        # Create sample accounts: 3 issuers x 3 email providers
        issuers = ["Binance", "Whitebit", "ByBit"]
        email_domains = ["gmail.com", "github.com", "microsoft.com"]

        sample_accounts = []
        for issuer in issuers:
            for domain in email_domains:
                email = f"user@{domain}"
                account = TOTPAccount.from_secret(
                    name=email,
                    secret=demo_secret,
                    password=demo_password,
                    issuer=issuer,
                    digits=6,
                    digest=DigestAlgorithm.SHA1,
                    interval=30,
                )
                sample_accounts.append(account)

        self.accounts_list.SetObjects(sample_accounts)

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

    def _on_add_account(self, event):
        """Handle Add Account menu item."""
        wx.MessageBox(
            "Add Account functionality not yet implemented",
            "Add Account",
            wx.OK | wx.ICON_INFORMATION,
        )

    def _on_delete_account(self, event):
        """Handle Delete Account menu item."""
        selected = self.accounts_list.GetSelectedObject()
        if selected is None:
            wx.MessageBox(
                "No account selected", "Delete Account", wx.OK | wx.ICON_WARNING
            )
            return

        wx.MessageBox(
            f"Delete functionality not yet implemented\nSelected: {selected.get_display_name()}",
            "Delete Account",
            wx.OK | wx.ICON_INFORMATION,
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
