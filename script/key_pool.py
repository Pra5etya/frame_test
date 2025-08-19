from config.logger import setup_logger
from script.generate_key import (
    first_runtime_key, key_pool, MAX_KEY_POOL, GRACE_PERIOD_SEC
)

import time, os

logger = setup_logger()

def reset_pool():
    global first_runtime_key

    # Ambil ORIGINAL KEY dari env (kalau ada)
    original_key = os.getenv("APP_MASTER_KEY")

    if original_key:
        key_pool.clear()  # Reset semua key lama
        key_pool.append((original_key, time.time()))

        first_runtime_key = original_key

        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info(f"[♻️] Key pool di-reset dengan ORIGINAL KEY: {original_key}")
    else:
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.warning("[⚠️] Tidak ada ORIGINAL KEY di environment saat reset.")

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # Tambahkan log jumlah & isi key
        logger.info(f"[📊] Jumlah key dalam pool setelah reset: {len(key_pool)}")
        logger.info(f"[🔑] Isi key_pool: {[k for k, _ in key_pool]}")


def cleanup_key_pool():
    global first_runtime_key  # penting supaya assignment ke modul aslinya

    now = time.time()

    # Hapus key pertama runtime ini kalau masih ada
    if first_runtime_key:
        for i, (k, ts) in enumerate(key_pool):
            if k == first_runtime_key:
                removed_key, _ = key_pool.pop(i)

                logger.info(f"[🗑] Key pertama runtime dihapus: {removed_key}")

                first_runtime_key = None
                break

    # Proses normal
    while len(key_pool) > MAX_KEY_POOL or (
        key_pool and now - key_pool[0][1] > GRACE_PERIOD_SEC
    ):
        removed_key, ts = key_pool.pop(0)
        logger.info(f"[🗑] Key lama dihapus dari pool: {removed_key}")

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # Tambahkan log jumlah & isi key
        logger.info(f"[📊] Jumlah key dalam pool setelah cleanup: {len(key_pool)}")
        logger.info(f"[🔑] Isi key_pool: {[k for k, _ in key_pool]}")
