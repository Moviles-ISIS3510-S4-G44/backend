from marketplace_andes_backend.app.core.config import get_settings
from marketplace_andes_backend.app.db.maintenance import clear_database


def main() -> None:
    settings = get_settings()
    clear_database(settings.database_url)
    print("Database cleared successfully.")


if __name__ == "__main__":
    main()
