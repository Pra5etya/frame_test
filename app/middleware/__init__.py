from .master import before_request_handler, after_request_handler

def register_middleware(app):
    """Registrasi middleware global"""

    @app.before_request
    def _before():
        # return before_request_handler()
        return 'before middleware'

    @app.after_request
    def _after(response):
        # return after_request_handler(response)
        return 'after middleware'

