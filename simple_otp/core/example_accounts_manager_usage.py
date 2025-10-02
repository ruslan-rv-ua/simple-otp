"""Example usage of AccountsManager for managing TOTP accounts."""

from simple_otp.core.accounts_manager import AccountsManager
from simple_otp.models.totp_account import DigestAlgorithm, TOTPAccount


def main():
    """Demonstrate AccountsManager usage."""

    # Initialize the manager (creates accounts.json one level up from
    # project if not exists)
    manager = AccountsManager()

    print(f"Storage location: {manager.get_storage_path()}\n")

    # List existing accounts (will show the example account on first run)
    print("=== Current Accounts ===")
    accounts = manager.list_accounts()
    for account in accounts:
        print(f"  - {account.get_display_name()}")
    print()

    # Add a new account
    print("=== Adding New Account ===")
    new_account = TOTPAccount.from_secret(
        name="myemail@gmail.com",
        secret="JBSWY3DPEHPK3PXP",  # Your actual TOTP secret
        password="my_master_password",  # Password to encrypt the secret
        issuer="Google",
        digits=6,
        digest=DigestAlgorithm.SHA1,
        interval=30,
    )

    try:
        manager.add_account(new_account)
        print(f"Added: {new_account.get_display_name()}\n")
    except ValueError as e:
        print(f"Account already exists: {e}\n")

    # Get a specific account
    print("=== Retrieving Specific Account ===")
    account = manager.get_account("myemail@gmail.com", "Google")
    if account:
        print(f"Found: {account.get_display_name()}")

        # Generate a TOTP code
        totp = account.get_totp("my_master_password")
        code = totp.now()
        print(f"Current TOTP code: {code}\n")

    # Update an account
    print("=== Updating Account ===")
    if account:
        updated_account = TOTPAccount.from_secret(
            name="newemail@gmail.com",  # Changed email
            secret="NEWSECRETKEY",
            password="my_master_password",
            issuer="Google",  # Same issuer
            digits=6,
        )

        success = manager.update_account("myemail@gmail.com", "Google", updated_account)

        if success:
            print("Account updated successfully\n")

    # List all accounts again
    print("=== All Accounts ===")
    accounts = manager.list_accounts()
    for account in accounts:
        print(f"  - {account.get_display_name()}")
    print()

    # Delete an account
    print("=== Deleting Account ===")
    deleted = manager.delete_account("newemail@gmail.com", "Google")
    if deleted:
        print("Account deleted successfully\n")

    # Clear all accounts (use with caution!)
    # count = manager.clear_all_accounts()
    # print(f"Cleared {count} accounts")


if __name__ == "__main__":
    main()
