# script/encrypt_env.py
from cryptography.fernet import Fernet
import os

def encrypt_env_file(input_path: str, output_path: str, secret_key: str):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Plaintext .env file not found: {input_path}")
    
    with open(input_path, "rb") as f:
        data = f.read()

    fernet = Fernet(secret_key)
    encrypted_data = fernet.encrypt(data)

    with open(output_path, "wb") as f:
        f.write(encrypted_data)

    print(f"✅ Encrypted: {input_path} -> {output_path}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise EnvironmentError("SECRET_KEY not found in .env")

    # Optional: dari argumen CLI atau fallback default
    import sys
    target_env = sys.argv[1] if len(sys.argv) > 1 else os.getenv("TARGET_ENV", "development")

    input_path = f"env/.env.{target_env}"
    output_path = f"lock/.env.{target_env}.enc"

    encrypt_env_file(input_path, output_path, secret_key)
