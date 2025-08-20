from config.logger import setup_logger
from script.generate_key import key_pool

from .session_store import create_session, get_session, delete_session
from .cookie_store import set_cookie, get_cookie, delete_cookie

from flask import request, g

logger = setup_logger()

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


def validate_session_and_cookie():
    """Validasi session Redis + cookie"""
    session_id = get_cookie() # ambil data dari cookie

    if not session_id:
        return False

    session_data = get_session(session_id) # data dari cookie diambil untuk session data
    logger.info(f"[VALIDATE] COOKIE={session_id}, SESSION={session_data}")

    if not session_data:
        return False

    return session_data.get("active_key") in [k[0] for k in key_pool]


# ==========================
# Lifecycle Middleware
# ==========================

def before_request_handler():
    """Cek session + cookie sebelum route dijalankan"""
    print("\n>>> [BEFORE_REQUEST] masuk middleware")

    print(f"➡️ Route: {request.endpoint} ({request.method} {request.path})")

    # print cookie yang masuk
    incoming_cookie = get_cookie()
    print(f"➡️ Cookie diterima: {incoming_cookie}")

    # ambil session di Redis kalau ada
    session_data = get_session(incoming_cookie) if incoming_cookie else None
    print(f"➡️ Session di Redis: {session_data}")

    if request.endpoint in WHITELIST_ROUTES:
        print("✅ Endpoint whitelist → dilewati\n")
        return

    latest_key = sign_key()
    if not latest_key:
        logger.warning("Tidak ada master key aktif")
        return None

    print("\n=== KEY POOL STATUS ===")
    for idx, (k, _) in enumerate(key_pool, start=1):
        print(f"[{idx}] {k}")
    print(f"Sign key (latest): {latest_key}\n")

    if not validate_session_and_cookie():
        print("❌ Session/cookie invalid → tandai reset")
        g.needs_reset = True

    else:
        print("✅ Session/cookie valid")
        g.needs_reset = False


def after_request_handler(response):
    """Inject session+cookie setelah response dibuat"""
    print(">>> [AFTER_REQUEST] masuk middleware")

    # print response status
    print(f"➡️ Response status: {response.status_code}")

    # print cookie yang akan dikirim
    outgoing_cookie = get_cookie()
    print(f"➡️ Cookie di response (sebelum reset): {outgoing_cookie}")

    if getattr(g, "needs_reset", False):
        latest_key = sign_key()
        if latest_key:
            print("⚠️ Reset session+cookie diperlukan")
            # destroy dulu
            session_id = get_cookie()
            if session_id:
                print(f"🗑️ Hapus session lama: {session_id}")
                delete_session(session_id)
                response = delete_cookie(response)

            # create baru
            new_sid = create_session(latest_key)
            print(f"✨ Buat session baru: {new_sid}")
            response = set_cookie(response, new_sid)
    else:
        print("✅ Tidak perlu reset session/cookie")

    # print cookie akhir di response
    print(f"➡️ Cookie akhir di response: {response.headers.get('Set-Cookie')}")
    print(">>> [AFTER_REQUEST] keluar middleware\n")
    return response