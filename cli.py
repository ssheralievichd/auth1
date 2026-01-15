import sys
from auth1.db.repositories import ApplicationRepository


def create_app():
    if len(sys.argv) < 4:
        print("Usage: python cli.py create-app <name> <allowed_hosts>")
        sys.exit(1)

    name = sys.argv[2]
    allowed_hosts = sys.argv[3]

    app = ApplicationRepository.create(name, allowed_hosts)

    print(f"Application created successfully!")
    print(f"Name: {app['name']}")
    print(f"Client ID: {app['client_id']}")
    print(f"Client Secret: {app['client_secret']}")
    print(f"Allowed Hosts: {app['allowed_hosts']}")


def list_apps():
    apps = ApplicationRepository.list_all()

    if not apps:
        print("No applications found")
        return

    for app in apps:
        print(f"\nClient ID: {app['client_id']}")
        print(f"Name: {app['name']}")
        print(f"Allowed Hosts: {app['allowed_hosts']}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <command>")
        print("Commands:")
        print("  create-app <name> <allowed_hosts>")
        print("  list-apps")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-app":
        create_app()
    elif command == "list-apps":
        list_apps()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    from auth1.db.connection import init_db
    init_db()
    main()
