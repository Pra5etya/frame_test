from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
from io import StringIO

def load_encrypted_env(env_name="dev"):
    env_map = {
        "dev": "env/.env.dev.enc",
        "stag": "env/.env.stag.enc",
        "pro": "env/.env.pro.enc",
    }

    env_path = env_map.get(env_name)
    key_path = "env/secret.key"

    if not os.path.exists(env_path):
        raise FileNotFoundError(f"File terenkripsi tidak ditemukan: {env_path}")

    with open(key_path, "rb") as f:
        key = f.read()

    fernet = Fernet(key)

    with open(env_path, "rb") as f:
        decrypted_data = fernet.decrypt(f.read())

    stream = StringIO(decrypted_data.decode())
    load_dotenv(stream=stream)
