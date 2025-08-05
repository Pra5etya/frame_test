from cryptography.fernet import Fernet
from script.encrypt import load_gcp_secret_key, load_aws_secret_key
from dotenv import load_dotenv
import os

# Step 1: Load .env utama
load_dotenv()

# Step 2: Dapatkan env dan direktori
env = os.getenv("FLASK_ENV") or "development"
ENV_DIR = os.getenv("ENV_DIR") or "environment"

# Step 3: Load .env.<env> dengan override
load_dotenv(f"{ENV_DIR}/.env.{env}", override=True)

# Step 4: Baru ambil variable yang dibutuhkan
INST_DIR = os.getenv("INST_DIR") 
LOCAL_KEY = os.getenv("LOCAL_KEY")
DEV_KEY = f"{INST_DIR}/{LOCAL_KEY}"


def generate_master_key():
    return Fernet.generate_key()

def write_dev_master_key(path=DEV_KEY):
    if os.path.exists(path):
        print(f"[✓] .masterkey sudah ada → {path}")
        return
    
    key = generate_master_key()
    with open(path, "wb") as f:
        f.write(key)

    print(f"[✓] .masterkey berhasil dibuat → {path}")

def set_staging_master_key():
    if os.getenv("APP_MASTER_KEY"):
        print("[✓] APP_MASTER_KEY sudah tersedia di environment.")
        return
    
    key = generate_master_key()
    os.environ["APP_MASTER_KEY"] = key.decode()

    print("[✓] APP_MASTER_KEY berhasil di-set sementara (runtime only).")

def ensure_staging_master_key():
    if "APP_MASTER_KEY" not in os.environ or not os.environ["APP_MASTER_KEY"]:
        print("[INFO] APP_MASTER_KEY tidak ditemukan di env, membuat baru...")
        set_staging_master_key()
        
    else:
        print("[✓] APP_MASTER_KEY tersedia di env.")

