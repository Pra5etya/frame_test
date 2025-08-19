from config.env_load import valid_and_update
from config.env_set import DevelopmentConfig, StagingConfig, ProductionConfig
from config.logger import setup_logger
from script.generate_key import key_pool

from datetime import timedelta
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

    # Set secret_key dari key_pool
    if key_pool:
        app.secret_key = key_pool[-1][0]
        
    else:
        app.secret_key = "fallback_secret"



    # # Konfigurasi cookie session pada FLASK
    # app.config.update(
    #     SESSION_COOKIE_NAME="myapp_session",
    #     SESSION_COOKIE_HTTPONLY=True,
    #     SESSION_COOKIE_SECURE=False,  # True jika HTTPS
    #     SESSION_COOKIE_SAMESITE='Lax'
    # )

    
    # app.config.update(
    # SESSION_COOKIE_NAME="myapp_session",
    # SESSION_COOKIE_DOMAIN=".example.com",
    # SESSION_COOKIE_PATH="/",
    # SESSION_COOKIE_HTTPONLY=True,
    # SESSION_COOKIE_SECURE=True,
    # SESSION_COOKIE_SAMESITE="Strict",
    # PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    # SESSION_REFRESH_EACH_REQUEST=False
    # )


    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        logger.info("=" * 30)
        logger.info(f"Use {resolved_env} configuration")
        logger.info(f"Loaded .env file: {env_path}")
        logger.info(f"Activate key from key-pool: {bool(key_pool)}")
        logger.info("=" * 30)
