import time
from config.logger import setup_logger
from script.generate_key import key_pool, MAX_KEY_POOL, GRACE_PERIOD_SEC

logger = setup_logger()

def cleanup_key_pool():
    now = time.time()
    while len(key_pool) > MAX_KEY_POOL or (
        key_pool and now - key_pool[0][1] > GRACE_PERIOD_SEC
    ):
        removed_key, ts = key_pool.pop(0)
        logger.info(f"[🗑] Key lama dihapus dari pool: {removed_key}")

def is_key_valid(input_key):
    now = time.time()
    for k, ts in key_pool:
        if k == input_key and now - ts <= GRACE_PERIOD_SEC:
            return True
    return False
