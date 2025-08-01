import os
import secrets
from dotenv import load_dotenv
from script.encrypt import encrypt_value, load_master_key
from script.manage_key import write_dev_master_key, set_staging_master_key

TARGET_KEYS = ["SECRET_KEY", "JWT_KEY", "CSRF_KEY"]

ALIASES = {
    "development": ["dev", "development"],
    "staging": ["stag", "staging"],
    "production": ["pro", "prod", "production"]
}

ENV_ALIASES = {alias: f".env.{env}" for env, aliases in ALIASES.items() for alias in aliases}

def generate_value():
    return secrets.token_hex(32)

def resolve_env_path(env_input: str, env_dir: str):
    resolved_env = ENV_ALIASES.get(env_input, f".env.{env_input}")
    env_path = os.path.join(env_dir, resolved_env)
    env_name = resolved_env.replace(".env.", "")
    return env_name, env_path

def initialize_master_key(env_name: str):
    if env_name == "development":
        write_dev_master_key()
    elif env_name == "staging":
        set_staging_master_key()
    elif env_name == "production":
        # Tambahan khusus jika butuh setup awal untuk production
        print("[INFO] Inisialisasi untuk environment production dilakukan.")
    else:
        raise ValueError(f"[ERROR] Environment tidak dikenali: {env_name}")

def load_env_and_master_key(env_path: str, env_name: str):
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
    else:
        print(f"[INFO] File {env_path} belum ada, akan dibuat.")
    return load_master_key(env_name)

def read_env_file(env_path: str):
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            return f.readlines()
    return []

def update_or_generate_keys(lines, key: bytes):
    new_lines = []
    found_keys = {k: False for k in TARGET_KEYS}

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)
            continue

        key_name, _, _ = line.partition("=")
        key_name = key_name.strip()

        if key_name in TARGET_KEYS:
            encrypted_val = encrypt_value(generate_value(), key)
            new_lines.append(f"{key_name}={encrypted_val}\n")
            found_keys[key_name] = True
        else:
            new_lines.append(line)

    # Tambahkan key yang belum ada
    for k, found in found_keys.items():
        if not found:
            encrypted_val = encrypt_value(generate_value(), key)
            new_lines.append(f"{k}={encrypted_val}\n")

    return new_lines

def write_env_file(env_path: str, new_lines):
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    print(f"[✓] File berhasil diperbarui → {env_path}")

def update_env_file(env_input: str, env_dir: str):
    env_name, env_path = resolve_env_path(env_input, env_dir)

    # Inisialisasi key & env vars sesuai env
    initialize_master_key(env_name)
    key = load_env_and_master_key(env_path, env_name)

    # Proses pembaruan .env
    lines = read_env_file(env_path)
    new_lines = update_or_generate_keys(lines, key)
    write_env_file(env_path, new_lines)
