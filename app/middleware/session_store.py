from config.logger import setup_logger
import redis, uuid

logger = setup_logger()

# ==========================
# Koneksi Redis
# ==========================
# Redis dipakai sebagai penyimpanan session server-side.
# Default: localhost:6379, DB 0
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

# Prefix untuk key di Redis biar lebih rapi
SESSION_PREFIX = "sess:"


# ==========================
# Session Helpers
# ==========================

def create_session(active_key):
    """
    Membuat session baru di Redis.
    - Generate session_id random (UUID).
    - Simpan ke Redis dengan key: sess:<session_id>
    - Value disimpan sebagai dict { "active_key": ... }
    - Return session_id untuk dipakai di cookie client.
    """
    session_id = str(uuid.uuid4())
    redis_key = f"{SESSION_PREFIX}{session_id}"

    redis_client.hset(redis_key, {"active_key": active_key})
    logger.info(f"[CREATE_SESSION] {session_id} -> {active_key}")

    # opsional: kasih TTL biar session auto-expire di Redis
    redis_client.expire(redis_key, 60 * 30)  # 30 menit

    return session_id


def get_session(session_id):
    """
    Ambil data session dari Redis berdasarkan session_id.
    - Jika session_id None → return None
    - Jika key tidak ada di Redis → return None
    - Kalau ada → return dict {"active_key": "..."}
    """
    if not session_id:
        return None

    redis_key = f"{SESSION_PREFIX}{session_id}"
    session_data = redis_client.hgetall(redis_key)

    if not session_data:
        logger.warning(f"[GET_SESSION] {session_id} tidak ditemukan di Redis")
        return None

    return session_data


def delete_session(session_id):
    """
    Hapus session dari Redis.
    - Jika key tidak ada, Redis abaikan.
    - Dipakai saat logout atau reset session.
    """
    if not session_id:
        return

    redis_key = f"{SESSION_PREFIX}{session_id}"
    redis_client.delete(redis_key)
    logger.info(f"[DELETE_SESSION] {session_id} dihapus dari Redis")
