from config.logger import setup_logger
from config.env_loader import load_env_files, CONFIG_MAP


def register_config():
    """
    Mengatur konfigurasi aplikasi berdasarkan environment yang dimuat.
    """
    env, env_file = load_env_files()
    logger = setup_logger()

    if env not in CONFIG_MAP:
        raise ValueError(f"Unsupported environment: {env}")

    selected_config = CONFIG_MAP[env]

    # Logging dan info
    print(f"\nUse {env} configuration")
    print("=" * 30)
    print(f"Loaded .env file: {env_file}")

    logger.info("=" * 30)
    logger.info(f"Use {env} configuration")
    logger.info(f"Loaded .env file: {env_file}")
    logger.info("=" * 30)

    return selected_config