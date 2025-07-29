from dotenv import load_dotenv
import os, sys, secrets

# === 1. Muat konfigurasi global dari file .env ===
# Misalnya: ENV_DIR=environment, INST_DIR=instance
load_dotenv(".env")  # variabel-variabel ini masuk ke os.environ

# Ambil nilai ENV_DIR dan INST_DIR dari .env
ENV_DIR = os.environ.get("ENV_DIR", "environment")  # direktori tempat file .env.[env] berada
INST_DIR = os.environ.get("INST_DIR", "instance")   # belum digunakan, tapi disiapkan untuk keperluan lain

# === 2. Alias lingkungan (environment) ===
# Dapat dipanggil dengan 'dev', 'development', dll
ALIASES = {
    "development": ["dev", "development"],
    "staging": ["stag", "staging"],
    "production": ["prod", "production"]
}

# Bangun mapping seperti: "dev" → ".env.development"
ENV_ALIASES = {
    alias: f".env.{env}"
    for env, aliases in ALIASES.items()
    for alias in aliases
}

# === 3. Key apa saja yang ingin digenerate ulang ===
TARGET_KEYS = ["SECRET_KEY", "JWT_KEY", "CSRF_KEY"]

# Fungsi untuk membuat key acak sepanjang 32 byte hex (256-bit)
def generate_value():
    return secrets.token_hex(32)

# Fungsi utama untuk memperbarui file .env
def update_env_file(env_input):
    # Cek apakah nama environment dikenali (dev, stag, prod, dll)
    filename = ENV_ALIASES.get(env_input)
    if not filename:
        print(f"[ERROR] Environment '{env_input}' tidak dikenali.")
        print("Gunakan salah satu dari:")

        for env, aliases in ALIASES.items():
            print(f"  {env}: {', '.join(aliases)}")

        sys.exit(1)

    # Bangun path lengkap ke file environment, contoh: environment/.env.development
    env_path = os.path.join(ENV_DIR, filename)

    # Jika file belum ada, mulai dari kosong
    if not os.path.exists(env_path):
        print(f"[INFO] File {env_path} belum ada, akan dibuat baru.")
        lines = []

    else:
        # Baca baris-baris yang ada di file
        with open(env_path, "r") as f:
            lines = f.readlines()

    new_lines = []
    updated_keys = set()

    # Iterasi tiap baris dalam file
    for line in lines:
        stripped = line.strip()

        # Lewati baris kosong atau komentar
        if not stripped or stripped.startswith("#") or "=" not in line:
            new_lines.append(line)
            continue

        # Pisahkan KEY=VALUE
        key, _, value = line.partition("=")
        key = key.strip()

        # Jika key termasuk yang ingin diupdate, ganti nilainya
        if key in TARGET_KEYS:
            new_value = generate_value()
            new_lines.append(f"{key}={new_value}\n")
            updated_keys.add(key)
            
        else:
            new_lines.append(line)

    # Tambahkan key yang belum ada sebelumnya
    for key in TARGET_KEYS:
        if key not in updated_keys:
            new_lines.append(f"{key}={generate_value()}\n")

    # Tulis ulang file dengan konten baru
    with open(env_path, "w") as f:
        f.writelines(new_lines)

    print(f"[✓] Secret keys berhasil diupdate untuk '{env_input}' → file: {env_path}")

# === 4. Entry point ===
if __name__ == "__main__":
    # Jika tidak ada argumen, default ke 'dev'
    env_arg = sys.argv[1].lower() if len(sys.argv) > 1 else "dev"
    update_env_file(env_arg)
