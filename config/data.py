# config/database.py
import os
from config.logger import setup_logger

logger = setup_logger()


def log_db_configuration(prefix):
    logger.info(f"Engine: {os.getenv(f'{prefix}_DB_ENGINE')}")
    logger.info(f"Driver: {os.getenv(f'{prefix}_DB_DRIVER', '')}")
    logger.info(f"Username: {os.getenv(f'{prefix}_DB_USERNAME', '')}")
    logger.info(f"Password: {'***' if os.getenv(f'{prefix}_DB_PASSWORD') else ''}")
    logger.info(f"Host: {os.getenv(f'{prefix}_DB_HOST', '')}")
    logger.info(f"Port: {os.getenv(f'{prefix}_DB_PORT', '')}")
    logger.info(f"DB Name: {os.getenv(f'{prefix}_DB_NAME')}")
    logger.info(f"DB Path: {os.getenv(f'{prefix}_DB_PATH')}")


def ensure_db_directory(db_path):
    db_dir_abs = os.path.abspath(db_path)
    if not os.path.exists(db_dir_abs):
        os.makedirs(db_dir_abs)
        logger.info(f"Database directory created at {db_dir_abs}")
    else:
        logger.info(f"Database directory already exists at {db_dir_abs}")
    return db_dir_abs


def resolve_sqlite_uri(prefix, db_dir_abs):
    db_name = os.getenv(f"{prefix}_DB_NAME")
    if not db_name:
        raise ValueError(f"{prefix}_DB_NAME must be set for SQLite.")

    db_file_path = os.path.join(db_dir_abs, db_name)

    if os.path.exists(db_file_path):
        logger.info(f"SQLite DB exists at {db_file_path}")
    else:
        logger.info(f"SQLite DB will be created at {db_file_path}")

    return f"sqlite:///{db_file_path}"


def resolve_remote_uri(prefix, db_dir_abs):
    engine = os.getenv(f"{prefix}_DB_ENGINE")
    driver = os.getenv(f"{prefix}_DB_DRIVER", "")
    username = os.getenv(f"{prefix}_DB_USERNAME", "")
    password = os.getenv(f"{prefix}_DB_PASSWORD", "")
    host = os.getenv(f"{prefix}_DB_HOST", "")
    port = os.getenv(f"{prefix}_DB_PORT", "")
    db_name = os.getenv(f"{prefix}_DB_NAME")

    if not db_name:
        raise ValueError(f"{prefix}_DB_NAME must be set for non-SQLite DB.")

    auth = f"{username}:{password}@" if username and password else ""
    port_part = f":{port}" if port else ""
    driver_part = f"+{driver}" if driver else ""
    host_part = f"{host}{port_part}" if host else ""

    return f"{engine}{driver_part}://{auth}{host_part}/{db_name}"


def resolve_database_uri(prefix: str) -> str:
    engine = os.getenv(f"{prefix}_DB_ENGINE")
    db_path = os.getenv(f"{prefix}_DB_PATH")

    log_db_configuration(prefix)
    db_dir_abs = ensure_db_directory(db_path)

    if engine == "sqlite":
        return resolve_sqlite_uri(prefix, db_dir_abs)
    return resolve_remote_uri(prefix, db_dir_abs)


def get_database_uri():
    env = os.getenv("FLASK_ENV", "").lower()
    prefix_map = {
        "development": "DEV",
        "staging": "STAGING",
        "production": "PROD",
        "test": "TEST"
    }

    prefix = prefix_map.get(env)
    if not prefix:
        raise ValueError(f"[ERROR] Unsupported FLASK_ENV: {env}")

    return resolve_database_uri(prefix)
