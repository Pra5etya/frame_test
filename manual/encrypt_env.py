from cryptography.fernet import Fernet
import os

ENV_FILES = {
    "dev": "env/.env.dev",
    "stag": "env/.env.stag",
    "pro": "env/.env.pro"
}

def get_or_create_key(mode):
    if mode == "dev":
        key_path = "env/secret.key"
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)
            print("🔑 Generated new key for dev at env/secret.key")
            return key
    else:
        key = os.getenv("SECRET_KEY_ENCRYPTION")
        if not key:
            raise EnvironmentError("SECRET_KEY_ENCRYPTION not found in env for staging/production.")
        return key.encode()

def encrypt_file(source, target, key):
    with open(source, "rb") as f:
        data = f.read()
    encrypted = Fernet(key).encrypt(data)
    with open(target, "wb") as f:
        f.write(encrypted)
    print(f"✅ Encrypted: {source} → {target}")

def main():
    for mode, file_path in ENV_FILES.items():
        if not os.path.exists(file_path):
            print(f"⚠️  File {file_path} tidak ditemukan, dilewati.")
            continue

        key = get_or_create_key(mode)
        encrypt_file(file_path, f"{file_path}.enc", key)

if __name__ == "__main__":
    main()
