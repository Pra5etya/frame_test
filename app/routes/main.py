from flask import Blueprint, render_template
from config.logger import setup_logger

main_bp = Blueprint('main', __name__)
logger = setup_logger()  # Inisialisasi log dari config/logger.py

@main_bp.route("/")
def index():
    logger.info(f"Memasuki tampilan dashboard")

    return render_template("index.html")

@main_bp.route("/unsupported")
def unsupported():

    return render_template("unsupported.html")