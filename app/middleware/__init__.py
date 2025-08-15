from .mk_required import key_checking

def register_middleware(app):
    """Registrasi semua middleware global."""
    
    @app.before_request
    def before_any_request():
        return key_checking()  # tambahkan return agar redirect langsung dieksekusi
