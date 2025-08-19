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
            if rotation_stop_event.wait(INTERVAL_MINUTES * 30): # settingan waktu untuk interval waktu
                break

            new_key = generate_master_key()
            os.environ["APP_MASTER_KEY"] = new_key.decode()
            key_pool.append((new_key.decode(), time.time()))

            cleanup_key_pool()
            
            logger.info(f"[🔄] SIGN-KEY di-rotate -> {os.environ['APP_MASTER_KEY']}")

            print(f'\nSIGN-KEY CHECK-1: {os.environ["APP_MASTER_KEY"]}')
            print(f'SIGN-KEY CHECK-2: {os.environ["APP_MASTER_KEY"]}\n')

            for i, item in enumerate(key_pool, start=1): 
                print(f"{i}. {item[0]}")

            print()


    threading.Thread(
        target=rotate_schedule,
        name="rotate_schedule",
        daemon=True
    ).start()

    logger.info("[⚙️] Key rotation aktif.")

def stop_thread():
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return

    rotation_stop_event.set()
    logger.info("[🛑] Key rotation & Server dihentikan.")

atexit.register(stop_thread)
