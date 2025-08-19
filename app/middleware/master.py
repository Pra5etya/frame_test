from flask import Flask, request, session, render_template, redirect, url_for, make_response
from flask_session import Session
import uuid

app = Flask(__name__)

# =========================
# Konfigurasi Flask-Session
# =========================
app.config["SECRET_KEY"] = "super-secret-key"
app.config["SESSION_TYPE"] = "filesystem"   # bisa diganti redis, mongodb, dll
app.config["SESSION_PERMANENT"] = False
Session(app)

# Cookie custom
COOKIE_NAME = "MYAPP_AUTH"

# Whitelist route (skip middleware auth)
WHITELIST = ["/forbidden", "/static"]


@app.before_request
def check_session_cookie():
    if request.path in WHITELIST:
        return

    # ambil cookie
    cookie_val = request.cookies.get(COOKIE_NAME)
    if not cookie_val:
        return redirect(url_for("forbidden"))

    # cek apakah cookie ada di server-side session
    if "sid" not in session or session.get("sid") != cookie_val:
        return redirect(url_for("forbidden"))


@app.route("/")
def index():
    # generate session id unik (server side session)
    session_id = str(uuid.uuid4())
    session["sid"] = session_id  # simpan di flask_session (server-side)

    # buat response
    resp = make_response(render_template("index.html"))
    # set cookie manual untuk validasi tambahan
    resp.set_cookie(COOKIE_NAME, session_id, httponly=True, samesite="Strict")

    return resp


@app.route("/forbidden")
def forbidden():
    return render_template("forbidden.html"), 403


if __name__ == "__main__":
    app.run(debug=True)
