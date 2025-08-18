from flask import request, session, redirect, url_for, make_response
from script.generate_key import key_pool
from config.logger import setup_logger

logger = setup_logger()

SESSION_KEY_NAME = "MASTER_KEY_AUTH"
COOKIE_NAME = "MASTER_KEY_AUTH"

WHITELIST_ROUTES = [
    "static",
    "main.forbidden",
    "main.unsupported",
]

# ==========================
# Helper
# ==========================

def get_active_key():
    return key_pool[-1][0] if key_pool else None

def set_session(active_key):
    """Simpan active_key ke Flask session"""
    logger.info("Menambahkan active_key ke session Flask")
    session[SESSION_KEY_NAME] = active_key

def validate_session(active_key):
    """Validasi session Flask"""
    session_key = session.get(SESSION_KEY_NAME)
    if not session_key:
        logger.warning("Session kosong")
        return False
    if session_key != active_key:
        logger.warning("Session tidak valid")
        return False
    return True

def set_cookie(resp, active_key):
    """Set custom cookie"""
    logger.info("Menambahkan cookie custom")
    resp.set_cookie(
        COOKIE_NAME,
        active_key,
        httponly=True,
        secure=False,   # True kalau HTTPS
        samesite="Lax"
    )
    return resp

def validate_cookie(active_key):
    """Validasi cookie custom"""
    cookie_val = request.cookies.get(COOKIE_NAME)
    if not cookie_val:
        logger.warning("Cookie tidak ditemukan")
        return False
    if cookie_val != active_key:
        logger.warning("Cookie tidak valid")
        return False
    return True

# ==========================
# Middleware
# ==========================

def key_checking():
    if request.endpoint in WHITELIST_ROUTES:
        return

    active_key = get_active_key()
    if not active_key:
        logger.warning("Tidak ada master key aktif")
        return redirect(url_for("main.forbidden"))

    # Validasi session + cookie
    valid_sess = validate_session(active_key)
    valid_cook = validate_cookie(active_key)

    if not (valid_sess and valid_cook):
        logger.warning("Session / cookie invalid → reset ulang")

        # Reset session
        session.clear()
        set_session(active_key)

        # Reset cookie
        resp = make_response(redirect(request.url))
        return set_cookie(resp, active_key)
