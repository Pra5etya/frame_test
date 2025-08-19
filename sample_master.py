from flask import request, g
from script.generate_key import key_pool
from config.logger import setup_logger
import uuid

logger = setup_logger()

COOKIE_NAME = "COOKIE_MK_AUTH"     # nama cookie custom

# Simpan session di memory (production: pakai Redis/DB)
custom_session_store = {}

WHITELIST_ROUTES = [
    "static",
    "main.forbidden",
    "main.unsupported",
]

# ==========================
# Helper
# ==========================

def sign_key():
    """Ambil key terbaru dari pool"""
    return key_pool[-1][0] if key_pool else None


def create_session(active_key):
    """Buat session baru di server store"""
    session_id = str(uuid.uuid4())
    custom_session_store[session_id] = {
        "active_key": active_key
    }
    logger.info(f"[CREATE_SESSION] {session_id} -> {active_key}")
    return session_id


def set_session_and_cookie(resp, active_key):
    """
    Simpan session di server + tambahkan cookie ke response
    """
    session_id = create_session(active_key)

    # cookie simpan session_id
    resp.set_cookie(
        COOKIE_NAME,
        session_id,
        httponly=True,
        secure=False,    # wajib True kalau sudah HTTPS
        samesite="Lax"
    )
    logger.info(f"[SET_COOKIE] {COOKIE_NAME} = {session_id}")
    return resp


def get_session_from_store():
    """Ambil data session dari server store pakai cookie"""
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        return None

    return custom_session_store.get(session_id)


def validate_session_and_cookie():
    """
    Validasi apakah session di server cocok dengan key_pool,
    dan cookie yang dikirim client valid
    """
    session_id = request.cookies.get(COOKIE_NAME)
    session_data = custom_session_store.get(session_id)

    logger.info(f"[VALIDATE] COOKIE {COOKIE_NAME}={session_id}, SESSION_DATA={session_data}")

    if not session_data:
        return False

    return session_data["active_key"] in [k[0] for k in key_pool]


def destroy_session_and_cookie(resp):
    """Hapus session di server + cookie di client"""
    session_id = request.cookies.get(COOKIE_NAME)
    if session_id and session_id in custom_session_store:
        del custom_session_store[session_id]
        logger.info(f"[DESTROY_SESSION] {session_id} dihapus")

    resp.delete_cookie(COOKIE_NAME)
    return resp

# ==========================
# Middleware Lifecycle
# ==========================

def before_request_handler():
    """Cek session + cookie sebelum route dijalankan"""
    print("\n>>> [BEFORE_REQUEST] Masuk middleware")

    if request.endpoint in WHITELIST_ROUTES:
        print(">>> [BEFORE_REQUEST] Endpoint dilewati (whitelist)")
        return

    latest_key = sign_key()
    if not latest_key:
        logger.warning("Tidak ada master key aktif")
        return None

    print("\n=== KEY POOL STATUS ===")
    for idx, (k, _) in enumerate(key_pool, start=1):
        print(f"[{idx}] {k}")
    print(f"Sign key (latest): {latest_key}\n")

    session_data = get_session_from_store()
    print(f"Session data: {session_data}")
    print("=======================\n")

    if not validate_session_and_cookie():
        print(">>> [BEFORE_REQUEST] Session/cookie invalid → tandai reset")
        g.needs_reset = True
    else:
        print(">>> [BEFORE_REQUEST] Session/cookie valid")
        g.needs_reset = False


def after_request_handler(response):
    """Inject session+cookie setelah response dibuat"""
    print(">>> [AFTER_REQUEST] Masuk middleware")

    if getattr(g, "needs_reset", False):
        latest_key = sign_key()
        if latest_key:
            print(">>> [AFTER_REQUEST] Reset session + cookie")
            response = destroy_session_and_cookie(response)
            response = set_session_and_cookie(response, latest_key)
    else:
        print(">>> [AFTER_REQUEST] Tidak perlu reset")

    print(">>> [AFTER_REQUEST] Keluar middleware\n")
    return response
