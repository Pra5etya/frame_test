from flask import request, session, redirect, url_for, current_app
from script.generate_key import key_pool
from config.logger import setup_logger

logger = setup_logger()

_last_active_key = None

def sync_flask_secret_key(app):
    global _last_active_key
    if key_pool:
        active_key = key_pool[-1][0]
        if active_key != _last_active_key:
            app.secret_key = active_key
            _last_active_key = active_key
            logger.info("Flask secret_key diperbarui dari key_pool.")
    else:
        logger.warning("Key pool kosong, secret key tetap.")


def key_checking():
    sync_flask_secret_key(current_app)

    WHITELIST_ROUTES = [
        "static",
        "main.login_key",
        "main.unsupported",
    ]

    if request.endpoint in WHITELIST_ROUTES:
        return

    if "key" not in session and key_pool:
        session["authenticated"] = False
        session["key"] = key_pool[-1][0]
        logger.info("Session awal dibuat otomatis.")

    if not session.get("authenticated") or session.get("key") != key_pool[-1][0]:
        logger.warning("Session tidak valid atau key berubah.")
        session.clear()
        return redirect(url_for("main.login_key"))
