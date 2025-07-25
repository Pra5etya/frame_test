from app.extension import db   # Guna menghindari circular import (yakni penggunaan import secara berlebihan)

class User(db.Model):  # Model User
    __tablename__ = "users"  # Nama tabel di DB

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)

    posts = db.relationship("Post", backref = "author", lazy = True)
    # Membuat relasi: 1 user bisa punya banyak post
    # "author" akan bisa digunakan dari post.author

    def __repr__(self):
        return f"<User {self.username}>"  # Untuk debug di console