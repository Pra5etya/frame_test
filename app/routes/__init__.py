def register_routes(app):
    from .main import main_bp
    from .auth import auth_bp
    from .post import post_bp

    app.register_blueprint(main_bp)     # landing page
    app.register_blueprint(auth_bp)     # /auth/endpoint
    app.register_blueprint(post_bp)     # /post/endpoint