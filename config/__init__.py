from config.env_load import valid_and_update  # Fungsi load_env yang baru
from config.env_set import DevelopmentConfig, StagingConfig, ProductionConfig
from config.logger import setup_logger  # Misal kamu punya setup_logger() sendiri

# Pemetaan environment ke konfigurasi
CONFIG_MAP = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig
}

def register_config():
    # Step 1: Siapkan logger
    logger = setup_logger()
    
    # Step 2: Load environment dan file .env terkait
    resolved_env, env_path = valid_and_update()

    # Step 3: Validasi dan pilih konfigurasi
    if resolved_env not in CONFIG_MAP:
        raise ValueError(f"Unsupported environment: {resolved_env}")

    # Step 4: Logging info
    print(f"\nUse {resolved_env} configuration")
    print("=" * 30)
    print(f"Loaded .env file: {resolved_env} \n")

    logger.info("=" * 30)
    logger.info(f"Use {resolved_env} configuration")
    logger.info(f"Loaded .env file: {env_path}")
    logger.info("=" * 30)
