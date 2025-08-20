from config.env_load import valid_and_update
from config.env_set import DevelopmentConfig, StagingConfig, ProductionConfig
from config.logger import setup_logger

import os

CONFIG_MAP = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig
}

def register_config(app):
    logger = setup_logger()
    resolved_env, env_path = valid_and_update()

    if resolved_env not in CONFIG_MAP:
        raise ValueError(f"Unsupported environment: {resolved_env}")

    app.config.from_object(CONFIG_MAP[resolved_env])

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        logger.info(f"Use {resolved_env} configuration")
        logger.info(f"Loaded .env file: {env_path} \n")
