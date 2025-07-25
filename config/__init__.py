from config.logger import setup_logger
from dotenv import load_dotenv
import os, sys


def load_env_files():
    """
    1. Memuat file .env utama dari root project (VALID_ENVS, DEFAULT_ENV, ENV_DIR)
    2. Lalu memuat file .env.{env} dari folder ENV_DIR
    3. Set FLASK_ENV dan return nama env-nya (lowercase)
    """

    # Step 1: load .env utama dari root project
    root_env_path = os.path.join(os.getcwd(), ".env")
    load_dotenv(dotenv_path = root_env_path, override = False)

    # Alias: untuk fleksibilitas pemanggilan via CLI atau DEFAULT_ENV
    alias_map = {
        "dev": "development",   # value dari map akan di terapkan pada register_config
        "stag": "staging",      # value dari map akan di terapkan pada register_config
        "pro": "production"     # value dari map akan di terapkan pada register_config
    }

    # Ambil konfigurasi dasar
    env_dir = os.getenv("ENV_DIR")
    valid_envs = set(os.getenv("VALID_ENVS").split(","))
    def_env = os.getenv("DEFAULT_ENV")

    # Step 2: Override dari command-line
    if len(sys.argv) > 1:
        def_env = sys.argv[1]

    # Konversi alias jika ada
    resolved_env = alias_map.get(def_env, def_env)

    # Step 3: load file .env.{env} sesuai environment
    env_file = os.path.join(env_dir, f".env.{resolved_env}")
    
    if os.path.exists(env_file):
        load_dotenv(dotenv_path = env_file, override = True)

    else:
        raise FileNotFoundError(f"Environment file not found: {env_file}")

    # Step 4: validasi ulang
    if resolved_env not in valid_envs:
        raise ValueError(f"Invalid environment '{def_env}' resolved to '{resolved_env}'. Allowed: {valid_envs}")

    os.environ["FLASK_ENV"] = resolved_env
    
    return resolved_env.lower(), env_file

def register_config():
    """
    Mendaftarkan dan mengembalikan konfigurasi berdasarkan environment hasil dari load_env_files.
    """

    env, env_file = load_env_files()
    logger = setup_logger()

    from config.set_env import (
        DevelopmentConfig,
        StagingConfig,
        ProductionConfig
    )

    config_map = {
        "development": DevelopmentConfig,
        "staging": StagingConfig,
        "production": ProductionConfig
    }

    if env not in config_map:
        raise ValueError(f"Unsupported environment: {env}")

    selected_config = config_map[env]

    print(f'\nUse {env} configuration')
    print('=' * 30)

    logger.info('=' * 30)
    logger.info(f'Use {env} configuration')
    logger.info('=' * 30)

    print(f'Loaded .env file: {env_file}')
    logger.info(f'Loaded .env file: {env_file}')

    return selected_config
