from script.generate_key import key_pool
from .master import before_request_handler, after_request_handler
from config.logger import setup_logger

import os, redis

def register_middleware(app):

    logger = setup_logger()

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        logger.info(f"Status Key: {bool(key_pool)} \n")

    # Set secret_key dari key_pool
    if key_pool:
        app.secret_key = key_pool[-1][0]
        
    else:
        app.secret_key = "fallback_secret"

    # Konfigurasi Flask-Session dengan Redis
    app.config["SESSION_TYPE"] = "redis"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True       # tanda tangan cookie agar aman
    app.config["SESSION_KEY_PREFIX"] = "sess:"    # prefix key di Redis
    app.config["SESSION_REDIS"] = redis.StrictRedis(host="localhost", port=6379, db=0)


    @app.before_request
    def _before():
        return before_request_handler()

    @app.after_request
    def _after(response):
        return after_request_handler(response)