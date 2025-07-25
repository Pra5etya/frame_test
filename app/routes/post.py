# from flask import Blueprint, render_template, redirect, url_for, flash, request
# from app.forms import PostForm
# from app.models import db, Post

# post_bp = Blueprint("post", __name__, url_prefix="/posts")

# @post_bp.route("/", methods=["GET"])
# def list_posts():
#     posts = Post.query.all()
#     return render_template("post_list.html", posts=posts)

# @post_bp.route("/create", methods=["GET", "POST"])
# def create_post():
#     form = PostForm()
#     if form.validate_on_submit():
#         post = Post(title=form.title.data, body=form.body.data, user_id=1)  # <- dummy user
#         db.session.add(post)
#         db.session.commit()
#         flash("Post created.")
#         return redirect(url_for("post.list_posts"))
#     return render_template("post_create.html", form=form)

from flask import Blueprint

post_bp = Blueprint('post', __name__, url_prefix='/post')

@post_bp.route('/data')
def post_page():
    return "Post Data Page"
