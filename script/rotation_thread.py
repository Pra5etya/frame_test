import os
import threading
import time
import atexit
from config.logger import setup_logger
from script.generate_key import (
    INTERVAL_MINUTES, rotation_lock, rotation_thread_event,
    rotation_stop_event, generate_master_key, key_pool
)
from script.key_pool import cleanup_key_pool

logger = setup_logger()

def start_thread():
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return

    with rotation_lock:
        if rotation_thread_event.is_set():
            return
        
        rotation_thread_event.set()

    def rotate_schedule():
        while not rotation_stop_event.is_set():
            if rotation_stop_event.wait(INTERVAL_MINUTES * 60):
                break

            new_key = generate_master_key()
            os.environ["APP_MASTER_KEY"] = new_key.decode()
            key_pool.append((new_key.decode(), time.time()))

            cleanup_key_pool()
            
            logger.info(f"[🔄] APP_MASTER_KEY di-rotate -> {os.environ['APP_MASTER_KEY']}")
            print(f'\nAPP_MASTER_KEY baru-1: {os.environ["APP_MASTER_KEY"]}')
            print(f'APP_MASTER_KEY baru-2: {os.environ["APP_MASTER_KEY"]}')

    threading.Thread(
        target=rotate_schedule,
        name="rotate_schedule",
        daemon=True
    ).start()

    logger.info("[⚙️] Key rotation thread aktif.")

def stop_thread():
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return

    rotation_stop_event.set()
    logger.info("[🛑] Key rotation thread dihentikan.")

atexit.register(stop_thread)
