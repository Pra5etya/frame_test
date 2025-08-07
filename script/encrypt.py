from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

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


def encrypt_value(value: str, key: bytes) -> str:
    if key is None:
        raise ValueError("Encryption key is None. Make sure the key is loaded properly.")

    else: 
        f = Fernet(key)
        token = f.encrypt(value.encode()).decode()
        
        return f"ENC({token})"


def load_master_key(env: str) -> bytes:
    if env == "development":
        return load_dev_key()
    
    elif env == "staging":
        return load_stag_key()
    
    elif env == "production":
        return load_pro_key()
    
    else:
        raise ValueError(f"Unknown environment: {env}")

def load_dev_key() -> bytes:
    DEV_KEY, _, _ = load_environment()

    with open(DEV_KEY, "rb") as f:
        return f.read()

def load_stag_key() -> bytes:
    return os.environ["APP_MASTER_KEY"].encode()

def load_pro_key() -> bytes:
    return os.environ["APP_MASTER_KEY"].encode()