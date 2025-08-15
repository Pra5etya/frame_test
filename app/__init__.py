from flask import Flask
from app.extension import db, migrate, login_manager

import os


def create_app():
    # =================
    # 0. core
    # =================

    core = Flask(__name__, 
                static_url_path = '/', 
                static_folder = 'static', 
                template_folder = 'templates')


    # =================
    # 2. config
    # =================

    # 2.1 log setup
    # =================

    from config.logger import setup_logger
    
    logger = setup_logger()

    # Hanya log "Restart" ketika proses utama berjalan setelah restart
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        logger.info("Flask is restarting...")
        logger.info("Log Start ...")


    # 2.2 env setup
    # =================

    from config import register_config

    configuration = register_config(core)

    # Terapkan ke Flask app 
    core.config.from_object(configuration)   


    # 2.3 middleware setup
    # =================

    from app.middleware import register_middleware

    register_middleware(core)


    # =================
    # 1. routes
    # =================

    from app.routes import register_routes

    register_routes(core)

    # # extension
    # db.init_app(core)
    # migrate.init_app(core, db)
    # login_manager.init_app(core)

    return core