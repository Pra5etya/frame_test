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
    print(f'data from current user: {CURRENT_USER}\n')

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
            logger.info(f"[✓] APP_MASTER_KEY sudah tersedia di environment. ORIGINAL KEY-> {os.environ["APP_MASTER_KEY"]}")
            print(f"\n[✓] APP_MASTER_KEY sudah tersedia di environment. ORIGINAL KEY-> {os.environ["APP_MASTER_KEY"]}\n")
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

# ========================== CONFIGURATION ==========================
INTERVAL_MINUTES = 1        # interval menit
MIN_KEY_POOL = 2            # minimal jumlah key di pool
MAX_KEY_POOL = 5            # maksimal jumlah key di pool
GRACE_PERIOD_SEC = 600      # key lama masih berlaku x detik setelah rotasi

CURRENT_USER = os.getenv("CURRENT_USER", "")  # user yang aktif di production
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "").split(",")


# ========================== STATE ==========================
rotation_thread_event = threading.Event()
rotation_lock = threading.Lock()
key_pool = []  # simpan (key_string, timestamp_created)


# ========================== IAM CHECK ==========================
def iam_check():
    """
    Pastikan CURRENT_USER diizinkan untuk mengakses key management.
    """
    if CURRENT_USER not in ALLOWED_USERS:
        logger.warning(
            f"[SECURITY] Unauthorized access attempt by user '{CURRENT_USER}'. "
            f"Allowed users: {ALLOWED_USERS}"
        )
        raise PermissionError(f"User '{CURRENT_USER}' tidak diizinkan mengakses key management.")



# ===================== ROTATION & THREAD =====================
import atexit

rotation_thread_event = threading.Event()  # menandakan thread aktif
rotation_stop_event = threading.Event()    # sinyal untuk menghentikan thread

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
    """
    Menghentikan thread rotasi key secara bersih.
    """
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        return

    rotation_stop_event.set()
    logger.info("[🛑] Key rotation thread & Server dihentikan.")
    

# Daftarkan stop_thread saat app keluar
atexit.register(stop_thread)


# ===================== KEY MANAGEMENT =====================
def prod_key():
    iam_check()  # cek IAM

    if os.getenv("APP_MASTER_KEY"):
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info(f"[✓] APP_MASTER_KEY sudah tersedia di environment. ORIGINAL KEY-> {os.environ["APP_MASTER_KEY"]}")
            print(f"\n[✓] APP_MASTER_KEY sudah tersedia di environment. ORIGINAL KEY-> {os.environ["APP_MASTER_KEY"]}\n")

    else:
        key = generate_master_key()
        os.environ["APP_MASTER_KEY"] = key.decode()
        key_pool.append((key.decode(), time.time()))

        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            logger.info("[✓] APP_MASTER_KEY berhasil di-set sementara (runtime only).")

    # Pastikan minimal key pool terisi
    while len(key_pool) < MIN_KEY_POOL:
        new_key = generate_master_key().decode()
        key_pool.append((new_key, time.time()))

    # Pastikan thread rotasi dimulai hanya sekali
    start_thread()

def check_prod_key():
    iam_check()
    key = os.getenv("APP_MASTER_KEY")

    if not key:
        logger.info("[INFO] APP_MASTER_KEY tidak ditemukan di env, membuat baru...")
        prod_key()
        return

    try:
        Fernet(key.encode())
        logger.info("[✓] APP_MASTER_KEY valid di environment.")
    except Exception as e:
        logger.error("[✗] APP_MASTER_KEY korup atau tidak valid.")
        logger.error(f"[Error] {e}")
        prod_key()

# ===================== POOL CLEANUP =====================
def cleanup_key_pool():
    now = time.time()
    while len(key_pool) > MAX_KEY_POOL or (
        key_pool and now - key_pool[0][1] > GRACE_PERIOD_SEC
    ):
        removed_key, ts = key_pool.pop(0)
        logger.info(f"[🗑] Key lama dihapus dari pool: {removed_key}")

# ===================== VALIDASI KEY REQUEST =====================
def is_key_valid(input_key):
    now = time.time()
    for k, ts in key_pool:
        if k == input_key and now - ts <= GRACE_PERIOD_SEC:
            return True
    return False