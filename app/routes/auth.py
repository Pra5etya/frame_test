# from flask import Blueprint, render_template, redirect, url_for, flash

# from app.forms import RegisterForm, LoginForm  # Ringkas & rapi
# from app.models import db, User

# from werkzeug.security import generate_password_hash, check_password_hash

# auth_bp = Blueprint("auth", __name__)

# @auth_bp.route("/register", methods=["GET", "POST"])
# def register():
#     form = RegisterForm()
#     if form.validate_on_submit():
#         existing_user = User.query.filter_by(username=form.username.data).first()
#         if existing_user:
#             flash("Username already exists.")
#             return redirect(url_for("auth.register"))

#         user = User(
#             username=form.username.data,
#             email=form.email.data,
#             password_hash=generate_password_hash(form.password.data)
#         )
#         db.session.add(user)
#         db.session.commit()
#         flash("Registration successful.")
#         return redirect(url_for("auth.login"))

#     return render_template("register.html", form=form)


# @auth_bp.route("/login", methods=["GET", "POST"])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and check_password_hash(user.password_hash, form.password.data):
#             flash("Login successful.")
#             return redirect(url_for("auth.login"))  # nanti bisa diarahkan ke dashboard
#         else:
#             flash("Invalid username or password.")
#             return redirect(url_for("auth.login"))

#     return render_template("login.html", form=form)

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix = '/auth')

@auth_bp.route('/login')
def login():
    return "Login Page"
