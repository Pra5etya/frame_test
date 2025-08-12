from cryptography.fernet import Fernet
from config.logger import setup_logger
from dotenv import load_dotenv

import os, time, threading

logger = setup_logger()

# ==========================
# ENVIRONMENT LOADER
# ==========================

def load_environment():
    """
    Load environment variables dari .env utama dan .env.<env>
    """
    # Step 1.1: Load .env utama
    load_dotenv()

    # Step 1.2: Dapatkan env dan direktori
    ENV_DIR = os.getenv("ENV_DIR", "")
    INST_DIR = os.getenv("INST_DIR") 
    LOCAL_KEY = os.getenv("LOCAL_KEY")

    FLASK_ENV = os.getenv("FLASK_ENV", "")

    # Step 1.3: Load .env.<env> dengan override (PINDAHKAN KE SINI)
    if FLASK_ENV:
        load_dotenv(f"{ENV_DIR}/.env.{FLASK_ENV}", override=True)

    # Step 1.4: Baru ambil variable yang dibutuhkan
    DEV_KEY = f"{INST_DIR}/{LOCAL_KEY}" if INST_DIR and LOCAL_KEY else None
    CURRENT_USER = os.getenv("CURRENT_USER")

    print(f'data from flask env: {FLASK_ENV}')
    print(f'data from current user: {CURRENT_USER}')

    return DEV_KEY, INST_DIR, CURRENT_USER








# ==========================
# MASTER KEY GENERATOR
# ==========================

def generate_master_key():
    """
    Generate kunci Fernet baru
    """
    return Fernet.generate_key()







# ==========================
# DEV KEY MANAGEMENT (.masterkey file)
# ==========================

def dev_key():
    """
    Membuat file .masterkey lokal jika belum ada.
    Jika folder instance belum ada, akan dibuat otomatis.
    """
    DEV_KEY, _, _ = load_environment()

    # Pastikan folder instance ada
    os.makedirs(os.path.dirname(DEV_KEY), exist_ok = True)

    if os.path.exists(DEV_KEY):
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info(f"[✓] .masterkey sudah ada → {DEV_KEY}")
        return

    else: 
        key = generate_master_key()

        with open(DEV_KEY, "wb") as f:
            f.write(key)
            
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info(f"[✓] .masterkey berhasil dibuat → {DEV_KEY}")

def check_dev_key():
    """
    Mengecek apakah .masterkey valid dan bisa digunakan
    """
    DEV_KEY, _, _ = load_environment()

    if not DEV_KEY or not os.path.exists(DEV_KEY):
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info(f"[!] .masterkey belum tersedia → {DEV_KEY}")
        return

    try:
        with open(DEV_KEY, "rb") as f:
            key = f.read()
            Fernet(key)  # validasi apakah key benar
        
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info(f"[✓] .masterkey valid → {DEV_KEY}")

    except Exception as e:
        logger.error(f"[✗] .masterkey korup atau tidak valid → {DEV_KEY}")
        logger.error(f"[Error] {e}")







# ==========================
# STAGING KEY MANAGEMENT (env var runtime only)
# ==========================

def stag_key():
    """
    Set APP_MASTER_KEY di environment runtime jika belum ada
    """
    if os.getenv("APP_MASTER_KEY"):
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info("[✓] APP_MASTER_KEY sudah tersedia di environment.")
        return

    else: 
        key = generate_master_key()
        os.environ["APP_MASTER_KEY"] = key.decode()
        
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info("[✓] APP_MASTER_KEY berhasil di-set sementara (runtime only).")
        
        print(f'APP_MASTER_KEY: {os.environ["APP_MASTER_KEY"]}')


def check_stag_key():
    """
    Mengecek apakah APP_MASTER_KEY valid dan bisa digunakan.
    Jika tidak ada, akan dibuat baru melalui stag_key().
    """
    key = os.getenv("APP_MASTER_KEY")

    if not key:
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info(f"[INFO] APP_MASTER_KEY tidak ditemukan di env, membuat baru...")

        stag_key()
        return  # stop setelah generate key baru

    try:
        Fernet(key.encode())  # validasi format key

        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info("[✓] APP_MASTER_KEY valid di environment.")

    except Exception as e:
        logger.error("[✗] APP_MASTER_KEY korup atau tidak valid.")
        logger.error(f"[Error] {e}")







# ==========================
# PRODUCTION KEY MANAGEMENT (env var runtime only)
# ==========================

# Global state
rotation_thread_event = threading.Event()
rotation_lock = threading.Lock()

# ===================== ROTATION & THREAD =====================

def start_thread(interval_minutes = 1):
    """
    Jalankan key rotation di background thread (hanya 1 kali per proses utama).
    """
    # Pastikan hanya proses utama Werkzeug yang menjalankan rotasi
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return
    
    print(f'ORIGINAL APP_MASTER_KEY: {os.environ["APP_MASTER_KEY"]}\n')

    with rotation_lock:
        if rotation_thread_event.is_set():
            # Thread sudah aktif → keluar tanpa bikin thread baru
            return
        rotation_thread_event.set()  # tandai sudah aktif

    def rotate_key_schedule():
        while True:
            time.sleep(interval_minutes * 60)

            new_key = generate_master_key()
            os.environ["APP_MASTER_KEY"] = new_key.decode()

            logger.info(f"[🔄] APP_MASTER_KEY di-rotate setiap {interval_minutes} menit. -> {os.environ["APP_MASTER_KEY"]}")

            print(f'APP_MASTER_KEY baru-1: {os.environ["APP_MASTER_KEY"]}')
            print(f'APP_MASTER_KEY baru-2: {os.environ["APP_MASTER_KEY"]}\n')

    threading.Thread(target=rotate_key_schedule, name="rotate_key_schedule", daemon=True).start()

    logger.info("[⚙️] Key rotation thread aktif.")

# ===================== KEY MANAGEMENT =====================
def prod_key():
    """
    Set APP_MASTER_KEY di environment runtime jika belum ada.
    """
    if os.getenv("APP_MASTER_KEY"):
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info("[✓] APP_MASTER_KEY sudah tersedia di environment.")
    
    else:
        key = generate_master_key()
        os.environ["APP_MASTER_KEY"] = key.decode()

        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info("[✓] APP_MASTER_KEY berhasil di-set sementara (runtime only).")

    # Pastikan thread rotasi dimulai hanya sekali
    start_thread()

def check_prod_key():
    """
    Mengecek apakah APP_MASTER_KEY valid dan bisa digunakan.
    Jika tidak ada, akan dibuat baru.
    """
    key = os.getenv("APP_MASTER_KEY")

    if not key:
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info("[INFO] APP_MASTER_KEY tidak ditemukan di env, membuat baru...")
        
        #
        prod_key()
        return

    try:
        Fernet(key.encode())
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info("[✓] APP_MASTER_KEY valid di environment.")

    except Exception as e:
        logger.error("[✗] APP_MASTER_KEY korup atau tidak valid.")
        logger.error(f"[Error] {e}")