from config.logger import setup_logger
import os

logger = setup_logger()  # Inisialisasi logger dari logger.py


def resolve_database_uri(prefix: str) -> str:
    """
    Menghasilkan SQLAlchemy Database URI berdasarkan environment prefix.
    Mencetak log konfigurasi DB dan membuat folder DB path jika perlu.
    """
    # 
    engine = os.getenv(f"{prefix}_DB_ENGINE")
    driver = os.getenv(f"{prefix}_DB_DRIVER", "").strip() or None
    username = os.getenv(f"{prefix}_DB_USERNAME", "").strip() or None
    password = os.getenv(f"{prefix}_DB_PASSWORD", "").strip() or None
    host = os.getenv(f"{prefix}_DB_HOST", "").strip() or None
    port = os.getenv(f"{prefix}_DB_PORT", "").strip() or None
    db_name = os.getenv(f"{prefix}_DB_NAME")
    db_path = os.getenv(f"{prefix}_DB_PATH")

    # 
    print(f'\nMenggunakan Engine: {engine}')
    print(f'Menggunakan Driver: {driver}')
    print(f'Menggunakan Username: {username}')
    print(f'Menggunakan Password: {password}')
    print(f'Menggunakan Host: {host}')
    print(f'Menggunakan Port: {port}')
    print(f'Nama Database: {db_name}')
    print(f'Path Database: {db_path}')

    # 
    logger.info(f"Engine: {engine}")
    logger.info(f"Driver: {driver}")
    logger.info(f"Username: {username}")
    logger.info(f"Password: {'***' if password else ''}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"DB Name: {db_name}")
    logger.info(f"DB Path: {db_path}")


    # Buat direktori storage untuk semua DB engine
    db_dir_abs = os.path.abspath(db_path)
    if not os.path.exists(db_dir_abs):
        os.makedirs(db_dir_abs)
        print(f"\n[INFO] Created database directory at {db_dir_abs}")
        logger.info(f"Database directory ready at {db_dir_abs}")

    else:
        print(f"\n[INFO] Database directory already exists at {db_dir_abs}")
        logger.info(f'Database directory already exists at {db_dir_abs}')


    # --- SQLite-specific logic ---
    if engine == "sqlite":
        if not db_name:
            raise ValueError(f"{prefix}_DB_NAME must be set for SQLite.")

        db_file_path = os.path.join(db_dir_abs, db_name)

        if os.path.exists(db_file_path):
            print(f"[INFO] SQLite database already exists at {db_file_path}. Skipping creation.\n")
            logger.info(f'SQLite database already exists at {db_file_path}. Skipping creation.')

        else:
            print(f"[INFO] SQLite database does not exist at {db_file_path}. It will be created when models are initialized.\n")
            logger.info(f'SQLite database does not exist at {db_file_path}. It will be created when models are initialized.')

        return f"sqlite:///{db_file_path}"

    # --- Non-SQLite logic (e.g., PostgreSQL, MySQL) ---
    if not db_name:
        raise ValueError(f"{prefix}_DB_NAME must be set for non-SQLite DB.")

    # 
    print(f"\n[INFO] Using remote database engine: {engine}{f'+{driver}' if driver else ''}")
    print(f"[INFO] Will connect to {host}:{port} as '{username}' to access database '{db_name}'")
    print(f"[INFO] Storage folder is ready at {db_dir_abs} (may be used for backup, logs, etc.)\n")

    # 
    logger.info(f"Using remote database engine: {engine}{f'+{driver}' if driver else ''}")
    logger.info(f"Will connect to {host}:{port} as '{username}' to access database '{db_name}'")
    logger.info(f"Storage folder is ready at {db_dir_abs} (may be used for backup, logs, etc.)")

    # 
    auth = f"{username}:{password}@" if username and password else ""
    port_part = f":{port}" if port else ""
    driver_part = f"+{driver}" if driver else ""
    host_part = f"{host}{port_part}" if host else ""

    return f"{engine}{driver_part}://{auth}{host_part}/{db_name}"


def get_database_uri():
    """
    Menentukan prefix berdasarkan FLASK_ENV, lalu panggil resolver DB.
    """

    env = os.getenv("FLASK_ENV").lower()

    prefix = {
        "development": "DEV",
        "staging": "STAGING",
        "production": "PROD",
        "test": "TEST"
    }.get(env)

    if not prefix:
        raise ValueError(f"[ERROR] Unsupported FLASK_ENV: {env}")

    return resolve_database_uri(prefix)