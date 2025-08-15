from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from config.logger import setup_logger
from script.generate_key import key_pool

main_bp = Blueprint('main', __name__)
logger = setup_logger()

@main_bp.route("/")
def index():
    logger.info("Memasuki halaman utama")
    return render_template("index.html")

@main_bp.route("/login-key", methods=["GET", "POST"])
def login_key():
    if request.method == "POST":
        input_key = request.form.get("key")

        if not key_pool:
            return "Tidak ada key aktif", 403

        active_key = key_pool[-1][0]

        if input_key == active_key:
            session["authenticated"] = True
            session["key"] = active_key
            return redirect(url_for("main.index"))
        
        else:
            return "Key salah!", 403

    return render_template("login.html")

@main_bp.route("/get-key")
def get_key():
    if not key_pool:
        return jsonify({"status": "error", "message": "Tidak ada key aktif"}), 404
    
    key = key_pool[-1][0]
    return jsonify({"status": "success", "api_key": key})

@main_bp.route("/secure")
def secure():
    active_keys = [k for k, _ in key_pool]
    return jsonify({
        "status": "success",
        "message": "Access granted to secure endpoint",
        "active_keys": active_keys
    })

@main_bp.route("/unsupported")
def unsupported():
    logger.info("Memasuki halaman unsupported")
    return render_template("unsupported.html")
