from marketplace_andes_backend.app.core.config import get_settings
from marketplace_andes_backend.app.db.maintenance import seed_database


def main() -> None:
    settings = get_settings()
    seed_database(settings.database_url)
    print("Database seeded successfully.")


if __name__ == "__main__":
    main()
