from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

import os, time, json

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
    FLASK_ENV = os.getenv("FLASK_ENV", "")
    ENV_DIR = os.getenv("ENV_DIR", "")

    # Step 1.3: Load .env.<env> dengan override (PINDAHKAN KE SINI)
    if FLASK_ENV:
        load_dotenv(f"{ENV_DIR}/.env.{FLASK_ENV}", override=True)

    # Step 1.4: Baru ambil variable yang dibutuhkan
    INST_DIR = os.getenv("INST_DIR") 
    LOCAL_KEY = os.getenv("LOCAL_KEY")
    DEV_KEY = f"{INST_DIR}/{LOCAL_KEY}" if INST_DIR and LOCAL_KEY else None
    CURRENT_USER = os.getenv("CURRENT_USER")

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
    Membuat file .masterkey lokal jika belum ada
    """
    DEV_KEY, _, _ = load_environment()

    if os.path.exists(DEV_KEY):
        print(f"\n[✓] .masterkey sudah ada → {DEV_KEY}")
        return

    key = generate_master_key()

    with open(DEV_KEY, "wb") as f:
        f.write(key)

    print(f"\n[✓] .masterkey berhasil dibuat → {DEV_KEY}")

def check_dev_key():
    """
    Mengecek apakah .masterkey valid dan bisa digunakan
    """
    DEV_KEY, _, _ = load_environment()

    if not DEV_KEY or not os.path.exists(DEV_KEY):
        print(f"\n[!] .masterkey belum tersedia → {DEV_KEY}")
        return

    try:
        with open(DEV_KEY, "rb") as f:
            key = f.read()
            Fernet(key)  # validasi apakah key benar

        print(f"\n[✓] .masterkey valid → {DEV_KEY}")

    except Exception as e:
        print(f"\n[✗] .masterkey korup atau tidak valid → {DEV_KEY}")
        print(f"[Error] {e}")

# ==========================
# STAGING KEY MANAGEMENT (env var runtime only)
# ==========================

def stag_key():
    """
    Set APP_MASTER_KEY di environment runtime jika belum ada
    """
    if os.getenv("APP_MASTER_KEY"):
        print("\n[✓] APP_MASTER_KEY sudah tersedia di environment.")
        return

    key = generate_master_key()
    os.environ["APP_MASTER_KEY"] = key.decode()

    print("\n[✓] APP_MASTER_KEY berhasil di-set sementara (runtime only).")


def check_stag_key():
    """
    Mengecek apakah APP_MASTER_KEY valid dan bisa digunakan.
    Jika tidak ada, akan dibuat baru melalui stag_key().
    """
    key = os.getenv("APP_MASTER_KEY")

    if not key:
        print(f"\n[INFO] APP_MASTER_KEY tidak ditemukan di env, membuat baru...")
        stag_key()
        return  # stop setelah generate key baru

    try:
        Fernet(key.encode())  # validasi format key
        print("\n[✓] APP_MASTER_KEY valid di environment.")

    except Exception as e:
        print("\n[✗] APP_MASTER_KEY korup atau tidak valid.")
        print(f"[Error] {e}")

# ==========================
# PRODUCTION KEY MANAGEMENT (env var runtime only)
# ==========================

def get_current_user():
    # IAM: User ID simulasi dari environment atau sesi login
    _, _, CURRENT_USER = load_environment()

    return CURRENT_USER or "guest"

def prod_key(force_rotate = False):
    """
    Set APP_MASTER_KEY di environment runtime jika belum ada, atau jika rotasi dipaksa.
    """
    _, DIR_INST, _ = load_environment()

    KEY_FILE = os.path.join(DIR_INST, "prod_master.key")
    EXPIRATION_SECONDS = 600  # 10 menit
    ALLOWED_USERS = ["admin", "superuser"]  # IAM simulasi

    # IAM check
    user = get_current_user()

    if user not in ALLOWED_USERS:
        print(f"\n[✗] Akses ditolak untuk user '{user}'. Hanya admin dapat membuat key.")

        return

    # Rotasi otomatis berdasarkan waktu
    if KEY_FILE.exists() and not force_rotate:
        try:
            with open(KEY_FILE, "r") as f:
                data = json.load(f)
                created_at = data.get("created_at", 0)

                if time.time() - created_at < EXPIRATION_SECONDS:
                    os.environ["APP_MASTER_KEY"] = data["key"]
                    print("\n[✓] APP_MASTER_KEY aktif dan masih valid.")

                    return
        except Exception as e:
            print(f"[!] Gagal membaca key file: {e}")

    # Generate baru
    key = generate_master_key().decode()
    os.environ["APP_MASTER_KEY"] = key

    # Simpan ke file terenkripsi (sementara dalam bentuk plaintext + waktu)
    KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(KEY_FILE, "w") as f:
        json.dump({"key": key, "created_at": time.time()}, f)

    print("\n[✓] APP_MASTER_KEY berhasil dibuat dan disimpan ke instance/.")


def check_prod_key():
    """
    Mengecek apakah APP_MASTER_KEY valid dan bisa digunakan.
    Jika tidak ada atau sudah expired, akan dibuat baru.
    """
    _, DIR_INST, _ = load_environment()

    KEY_FILE = os.path.join(DIR_INST, "prod_master.key")
    EXPIRATION_SECONDS = 600  # 10 menit

    key = os.getenv("APP_MASTER_KEY")

    if not key:
        print(f"\n[INFO] APP_MASTER_KEY tidak ditemukan di runtime, mencoba ambil dari instance...")
        try:
            with open(KEY_FILE, "r") as f:
                data = json.load(f)
                key = data["key"]
                created_at = data.get("created_at", 0)

                if time.time() - created_at > EXPIRATION_SECONDS:
                    print("[INFO] APP_MASTER_KEY kadaluarsa, membuat baru...")
                    prod_key(force_rotate=True)

                    return

                os.environ["APP_MASTER_KEY"] = key
                print("\n[✓] APP_MASTER_KEY berhasil di-set dari file instance.")

        except FileNotFoundError:
            print("[INFO] File key tidak ditemukan, membuat baru...")
            prod_key()

        except Exception as e:
            print("[✗] Gagal membaca key dari file.")
            print(f"[Error] {e}")
            prod_key()

        return

    # Validasi format key
    try:
        Fernet(key.encode())
        print("\n[✓] APP_MASTER_KEY valid di environment.")

    except InvalidToken:
        print("\n[✗] APP_MASTER_KEY tidak valid, merotasi...")
        prod_key(force_rotate=True)

    except Exception as e:
        print(f"\n[✗] APP_MASTER_KEY error.\n[Error] {e}")
        prod_key(force_rotate=True)
