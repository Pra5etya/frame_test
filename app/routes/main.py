from flask import Blueprint, render_template, jsonify, make_response
from config.logger import setup_logger
from script.generate_key import key_pool
from app.middleware.mk_required import get_active_key, set_session, set_cookie

main_bp = Blueprint('main', __name__)
logger = setup_logger()

@main_bp.route("/")
def index():
    logger.info("Memasuki halaman utama")
    active_key = get_active_key()
    if not active_key:
        return render_template("forbidden.html"), 403

    # inject session + cookie
    set_session(active_key)
    resp = make_response(render_template("index.html"))
    return set_cookie(resp, active_key)

@main_bp.route("/secure")
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
    logger.info("Memasuki halaman unsupported")
    return render_template("unsupported.html")
