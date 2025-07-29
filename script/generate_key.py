import os, secrets

# Target key yang harus ada
TARGET_KEYS = ["SECRET_KEY", "JWT_KEY", "CSRF_KEY"]

# Alias env ke file .env
ALIASES = {
    "development": ["dev", "development"],
    "staging": ["stag", "staging"],
    "production": ["pro", "prod", "production"]
}

ENV_ALIASES = {
    alias: f".env.{env}" for env, aliases in ALIASES.items() for alias in aliases
}

def generate_value() -> str:
    """Generate 256-bit secure hex string"""
    return secrets.token_hex(32)


def update_env_file(env_input: str, env_dir: str):
    """Update atau buat file .env.[env] dengan secret key jika belum ada"""
    filename = ENV_ALIASES.get(env_input, f".env.{env_input}")
    env_path = os.path.join(env_dir, filename)

    if not os.path.exists(env_path):
        print(f"[INFO] File {env_path} tidak ditemukan, akan dibuat baru.")
        lines = []
    else:
        with open(env_path, "r") as f:
            lines = f.readlines()

    new_lines = []
    found_keys = {key: False for key in TARGET_KEYS}

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)
            continue

        key, _, _ = line.partition("=")
        key = key.strip()

        if key in TARGET_KEYS:
            new_lines.append(f"{key}={generate_value()}\n")
            found_keys[key] = True

        else:
            new_lines.append(line)

    # Tambahkan jika belum ada
    for key, found in found_keys.items():
        if not found:
            new_lines.append(f"{key}={generate_value()}\n")

    os.makedirs(env_dir, exist_ok=True)

    with open(env_path, "w") as f:
        f.writelines(new_lines)

    print(f"[✓] Secret keys berhasil diupdate untuk '{env_input}' → {env_path}")