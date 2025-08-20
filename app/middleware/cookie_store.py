from flask import request

COOKIE_NAME = "COOKIE_MK_AUTH"   # nama cookie yang dipakai app


# ==========================
# Cookie Helpers
# ==========================

def set_cookie(response, session_id):
    """
    Simpan session_id ke cookie client.
    - response: object Flask Response
    - session_id: string UUID dari session Redis
    - Diset dengan atribut keamanan dasar:
        httponly=True  → tidak bisa diakses JavaScript
        secure=False   → wajib True jika pakai HTTPS
        samesite="Lax" → aman untuk CSRF dasar
    """
    response.set_cookie(
        COOKIE_NAME,
        session_id,
        httponly=True,
        secure=False,    # ⚠️ ubah ke True kalau sudah pakai HTTPS
        samesite="Lax"
    )
    return response


def get_cookie():
    """
    Ambil nilai cookie dari request client.
    - return None kalau cookie tidak ada
    - return session_id string kalau ada
    """
    return request.cookies.get(COOKIE_NAME)


def delete_cookie(response):
    """
    Hapus cookie dari browser client.
    - Biasanya dipakai saat logout atau reset session.
    """
    response.delete_cookie(COOKIE_NAME)
    return response
