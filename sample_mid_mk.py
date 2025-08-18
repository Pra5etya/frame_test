from flask import request, session, redirect, url_for, make_response, current_app
from script.generate_key import key_pool
from config.logger import setup_logger

import time
import uuid
from urllib.parse import urlencode
from functools import wraps

logger = setup_logger()

# ==========================
# Konstanta & Konfigurasi
# ==========================
SESSION_KEY_NAME   = "MASTER_KEY_AUTH"   # nama key di Flask session
COOKIE_NAME        = "MASTER_KEY_AUTH"   # nama cookie token
USER_COOKIE_NAME   = "USER_ID"           # cookie identitas user anonim
BOOTSTRAP_COOKIE   = "MK_BOOTSTRAPPED"   # anti redirect loop (short lived)

# Route yang tidak butuh validasi
WHITELIST_ROUTES = [
    "static",
    "main.forbidden",
    "main.unsupported",
]

# TTL token (detik)
DEFAULT_TOKEN_TTL = 30 * 60  # 30 menit
# Scope default user
DEFAULT_SCOPE = "basic"


# ==========================
# Util kecil
# ==========================
def _now() -> int:
    return int(time.time())

def _anti_loop_active() -> bool:
    """Cek apakah request ini hasil redirect (untuk cegah infinite loop)."""
    return (request.args.get("_mk") == "1") or (request.cookies.get(BOOTSTRAP_COOKIE) == "1")

def _bounce_url_once():
    """Tambah query flag _mk=1 agar redirect hanya sekali."""
    args = dict(request.args or {})
    args["_mk"] = "1"
    return f"{request.path}?{urlencode(args)}"


# ==========================
# Active key & User identity
# ==========================
def get_active_key():
    """Ambil master key aktif (rotasi = elemen terakhir key_pool)."""
    return key_pool[-1][0] if key_pool else None

def get_or_set_user_id(resp=None) -> (str, object):
    """Ambil/buat USER_ID unik (UUID) yang disimpan di cookie USER_ID."""
    uid = request.cookies.get(USER_COOKIE_NAME)
    if uid:
        return uid, resp
    uid = str(uuid.uuid4())
    logger.info(f"Generate USER_ID baru: {uid}")
    if resp is None:
        resp = make_response()
    resp.set_cookie(
        USER_COOKIE_NAME,
        uid,
        httponly=False,     # supaya bisa dilihat di DevTools / JS
        secure=False,       # set True di production (HTTPS)
        samesite="Lax",
        max_age=365 * 24 * 3600,  # 1 tahun
    )
    return uid, resp


# ==========================
# Token (Cookie + Session)
# ==========================
# Format token: "key|user_id|iat|exp|scope"
# iat = issued at, exp = expiry
def build_token(active_key: str, user_id: str, ttl: int = DEFAULT_TOKEN_TTL, scope: str = DEFAULT_SCOPE):
    iat = _now()
    exp = iat + ttl
    token = f"{active_key}|{user_id}|{iat}|{exp}|{scope}"
    return token, iat, exp

def parse_token(token: str):
    try:
        key, user_id, iat, exp, scope = token.split("|", 4)
        return {
            "key": key,
            "user_id": user_id,
            "iat": int(iat),
            "exp": int(exp),
            "scope": scope
        }
    except Exception:
        return None

def set_session_from_token(token_data: dict):
    """Mirror payload token ke Flask session."""
    session.clear()
    session[SESSION_KEY_NAME] = {
        "key": token_data["key"],
        "user_id": token_data["user_id"],
        "exp": token_data["exp"],
        "scope": token_data["scope"],
    }
    logger.info("Session diisi dari token")

def validate_session_against(active_key: str) -> bool:
    """Cek apakah session masih valid (key sama + belum expired)."""
    data = session.get(SESSION_KEY_NAME)
    if not data:
        return False
    if data.get("key") != active_key:
        return False
    if data.get("exp", 0) <= _now():
        return False
    return True

def set_cookie_token(resp, token: str, exp_epoch: int):
    """Simpan token di cookie + short-lived bootstrap cookie (anti loop)."""
    max_age = max(0, exp_epoch - _now())
    resp.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,  # tidak bisa dibaca JS
        secure=False,
        samesite="Lax",
        max_age=max_age,
    )
    resp.set_cookie(
        BOOTSTRAP_COOKIE,
        "1",
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=5,
    )
    return resp

def validate_cookie_against(active_key: str) -> (bool, dict | None):
    """Validasi cookie token terhadap active_key & expiry."""
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return False, None
    data = parse_token(raw)
    if not data:
        return False, None
    if data["key"] != active_key:
        return False, data
    if data["exp"] <= _now():
        return False, data
    return True, data


# ==========================
# Refresh / Rotate
# ==========================
def refresh_all_and_redirect(active_key: str, scope: str = DEFAULT_SCOPE):
    """
    Refresh / rotasi token:
      - Pastikan user_id ada
      - Buat token baru
      - Sinkronkan ke Session + Cookie
      - Redirect sekali (anti loop)
    """
    target = request.path if _anti_loop_active() else _bounce_url_once()
    resp = make_response(redirect(target))
    user_id, resp = get_or_set_user_id(resp)
    token, iat, exp = build_token(active_key, user_id, ttl=DEFAULT_TOKEN_TTL, scope=scope)

    set_session_from_token({
        "key": active_key,
        "user_id": user_id,
        "iat": iat,
        "exp": exp,
        "scope": scope
    })
    resp = set_cookie_token(resp, token, exp)
    return resp


# ==========================
# Middleware utama
# ==========================
def key_checking():
    """
    Middleware validasi:
      - Wajib ada active_key
      - Session & Cookie diverifikasi
      - Jika invalid → refresh/rotasi
      - Cegah infinite redirect
    """
    if request.endpoint in WHITELIST_ROUTES:
        return
    active_key = get_active_key()
    if not active_key:
        return redirect(url_for("main.forbidden"))

    cookie_ok, cookie_data = validate_cookie_against(active_key)
    session_ok = validate_session_against(active_key)

    if cookie_ok and session_ok:
        return  # aman, lanjut request

    if _anti_loop_active():
        return redirect(url_for("main.forbidden"))

    return refresh_all_and_redirect(active_key, scope=(cookie_data["scope"] if cookie_data else DEFAULT_SCOPE))


# ==========================
# Strict Mode: Scope Checking
# ==========================
def require_scope(required_scope: str):
    """
    Decorator untuk melindungi route.
    Hanya user dengan scope >= required_scope yang bisa akses.
    """
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = session.get(SESSION_KEY_NAME)
            if not data:
                logger.warning("Strict mode: session kosong")
                return redirect(url_for("main.forbidden"))

            user_scope = data.get("scope")
            if not user_scope:
                return redirect(url_for("main.forbidden"))

            # Implementasi simple: harus exact match
            if user_scope != required_scope:
                logger.warning(f"Strict mode: scope {user_scope} ≠ {required_scope}")
                return redirect(url_for("main.forbidden"))

            return f(*args, **kwargs)
        return decorated
    return wrapper
