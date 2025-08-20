from flask import Blueprint, render_template, jsonify, request, make_response
from config.logger import setup_logger
from script.generate_key import key_pool

from ..middleware.master import sign_key
from ..middleware.session_store import get_session


main_bp = Blueprint('main', __name__)
logger = setup_logger()

@main_bp.route("/")
def index():
    logger.info("Memasuki halaman utama")

    # ambil sign key terbaru
    latest_key = sign_key()

    # ambil cookie dari request
    cookie_key = request.cookies.get("COOKIE_MK_AUTH")

    # ambil session dari Redis berdasarkan cookie_key
    session_data = get_session(cookie_key) if cookie_key else None
    session_key = session_data["active_key"] if session_data else None

    return render_template(
        "index.html",
        latest_key=latest_key,
        session_key=session_key,
        cookie_key=cookie_key,
    )

@main_bp.route("/test_keypool")
def secure():
    active_keys = [k for k, _ in key_pool]
    return jsonify({
        "status": "success",
        "message": "Access granted",
        "active_keys": active_keys
    })

@main_bp.route("/forbidden")
def forbidden():
    logger.warning("Akses ditolak: user tidak punya izin")
    return render_template("forbidden.html"), 403


@main_bp.route("/unsupported")
def unsupported():
    logger.warning("Memasuki halaman unsupported")
    return render_template("unsupported.html"), 406
