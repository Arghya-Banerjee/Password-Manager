import argparse
import getpass

from password_manager.vault import init_vault, load_vault, save_vault
from password_manager.utils import generate_password

def main():
    parser = argparse.ArgumentParser(prog="pm-cli")
    subs = parser.add_subparsers(dest="command")

    # init
    subs.add_parser("init", help="Initialize a new vault")

    # add
    add_p = subs.add_parser("add", help="Add or update an entry")
    add_p.add_argument("service", help="Name of the service (e.g. example.com)")
    add_p.add_argument("-u", "--username", help="Username or email")
    add_p.add_argument("-p", "--password", help="Password")
    add_p.add_argument("--generate", action="store_true",
                       help="Generate a random password")
    add_p.add_argument("-l", "--length", type=int, default=16,
                       help="Length of generated password")

    # get
    get_p = subs.add_parser("get", help="Retrieve credentials")
    get_p.add_argument("service", help="Name of the service")

    # list
    subs.add_parser("list", help="List all saved services")

    args = parser.parse_args()

    if args.command == "init":
        mp = getpass.getpass("Master password: ")
        init_vault(mp)
        print("Vault initialized.")
        return

    # for add/get/list we need to unlock
    mp = getpass.getpass("Master password: ")
    vault = load_vault(mp)

    if args.command == "add":
        svc = args.service
        user = args.username or input("Username: ")
        if args.generate:
            pwd = generate_password(args.length)
            print(f"Generated: {pwd}")
        else:
            pwd = args.password or getpass.getpass("Password: ")
        vault[svc] = {"username": user, "password": pwd}
        save_vault(mp, vault)
        print(f"Saved entry for '{svc}'.")

    elif args.command == "get":
        entry = vault.get(args.service)
        if not entry:
            print(f"No entry found for '{args.service}'.")
        else:
            print(f"Service: {args.service}")
            print(f"Username: {entry['username']}")
            print(f"Password: {entry['password']}")

    elif args.command == "list":
        print("Saved services:")
        for svc in vault.keys():
            print(f"  • {svc}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
