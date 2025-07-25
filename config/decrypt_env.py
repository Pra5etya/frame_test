from cryptography.fernet import Fernet
import os

def decrypt_env_file(encrypted_path: str, secret_key: str) -> str:
    if not os.path.exists(encrypted_path):
        raise FileNotFoundError(f"Encrypted .env file not found: {encrypted_path}")
    
    with open(encrypted_path, "rb") as file:
        encrypted_data = file.read()

    try:
        fernet = Fernet(secret_key)
        return fernet.decrypt(encrypted_data).decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt env file: {e}")
