from config.logger import setup_logger
from config.env_loader import load_env_files, CONFIG_MAP
import os


def register_config():
    """
    Mengatur konfigurasi aplikasi berdasarkan environment yang dimuat.
    """
    env, env_file = load_env_files()
    provider = os.getenv("SECRET_PROVIDER")  # ← Ambil dari environment
    logger = setup_logger()

    if env not in CONFIG_MAP:
        raise ValueError(f"Unsupported environment: {env}")

    selected_config = CONFIG_MAP[env]

    # Logging dan info
    print(f"\nUse {env} configuration")
    print("=" * 30)
    print(f"Loaded .env file: {env_file}")
    print(f"Secret Provider: {provider}")  # ← Info tambahan

    logger.info("=" * 30)
    logger.info(f"Use {env} configuration")
    logger.info(f"Loaded .env file: {env_file}")
    logger.info(f"Secret Provider: {provider}")
    logger.info("=" * 30)

    return selected_config
