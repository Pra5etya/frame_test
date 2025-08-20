# Meng-enkripsi file utama guna melindungi value dari environment
from script.generate_key import dev_key, stag_key, prod_key

# Meng-enkripsi nilai secret pada environment
from script.encrypt import encrypt_value, load_master_key

from config.logger import setup_logger
from dotenv import load_dotenv

import os, secrets


# Key yang ingin diamankan (akan dibuat otomatis jika belum ada)
TARGET_KEYS = ["SECRET_KEY", "JWT_KEY", "CSRF_KEY"]

# Alias nama environment untuk pemetaan argumen CLI ke nama sebenarnya
ALIAS = {
    "development": ["d", "dev"],
    "staging": ["s", "stag"],
    "production": ["p", "pro", "prod"]
}

# Membalik ALIAS menjadi peta {alias: nama_environment}
ALIAS_MAP = {alias: env for env, aliases in ALIAS.items() for alias in aliases}


# ------------------------
# Fungsi: Inisialisasi Master Key berdasarkan environment
# ------------------------

def init_master_key(env_name: str):
    if env_name == "development":
        dev_key()  # Master key disimpan sebagai file lokal (.masterkey)

    elif env_name == "staging":
        stag_key()  # Master key didapat dari environment variable `APP_MASTER_KEY`

    elif env_name == "production":
        prod_key()  # Master key diperoleh dari Secret Manager (misalnya vendor(GCP/AWS) atau buat sendiri)

    else:
        raise ValueError(f"[ERROR] Environment tidak dikenali: {env_name}")


# ------------------------
# Fungsi: Resolve input environment dan ambil master key
# ------------------------

def resolve_env(env_input: str, env_dir: str):
    env_file = ALIAS_MAP.get(env_input, f".env.{env_input}")  # Tentukan nama file .env
    env_path = os.path.join(env_dir, env_file)                # Gabungkan dengan direktori
    env_name = env_file.replace(".env.", "")                  # Ambil nama environment (tanpa .env.)

    init_master_key(env_name)  # Inisialisasi master key sesuai env

    # Jika file .env sudah ada, muat variabelnya
    if os.path.exists(env_path):
        load_dotenv(env_path, override = True)

    else:
        print(f"[INFO] File {env_path} belum ada, akan dibuat.")

    # Ambil master key terenkripsi dalam bentuk byte
    key = load_master_key(env_name)

    return env_path, key


# ------------------------
# Fungsi: Membaca isi file .env (jika ada)
# ------------------------

def read_env_lines(env_path: str):
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
            
            # print("[INFO] Isi file .env:")

            # for line in lines:
            #     print(line.strip())

            return lines
    return []


# ------------------------
# Fungsi: Proses isi file .env dan enkripsi value dari TARGET_KEYS
# ------------------------

def process_env_lines(lines, key: bytes):
    """
    Memproses baris-baris file .env:
    - Mengenkripsi ulang TARGET_KEYS dengan nilai acak baru
    - Menandai key yang sudah ditemukan
    - Baris lain tetap dipertahankan
    """
    new_lines = []
    found_keys = {k: False for k in TARGET_KEYS}

    for line in lines:
        stripped = line.strip()

        # Lewati baris kosong, komentar, atau baris tidak valid
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            new_lines.append(line)

            continue

        key_name, _, _ = line.partition("=")
        key_name = key_name.strip()

        # Jika key termasuk yang ditargetkan, enkripsi nilai baru
        if key_name in TARGET_KEYS:
            encrypted = encrypt_value(secrets.token_hex(32), key)
            new_lines.append(f"{key_name}={encrypted}\n")
            found_keys[key_name] = True

        else:
            # Key lain tetap ditulis ulang tanpa perubahan
            new_lines.append(line)

    return new_lines, found_keys


# ------------------------
# Fungsi: Menambahkan key yang belum ada ke file
# ------------------------

def add_missing_keys(existing_lines, found_keys, key: bytes):
    """
    Menambahkan baris baru ke file untuk key yang belum ditemukan.
    Setiap key akan memiliki nilai acak yang terenkripsi.
    """
    for k, found in found_keys.items():
        if not found:
            encrypted = encrypt_value(secrets.token_hex(32), key)
            existing_lines.append(f"{k}={encrypted}\n")

    return existing_lines


# ------------------------
# Fungsi Utama: Update file .env
# ------------------------

def update_env_file(env_input: str, env_dir: str):
    """
    Fungsi utama untuk:
    - Mengambil path file dan master key
    - Membaca dan memproses isi file
    - Mengenkripsi ulang key yang ditentukan
    - Menambahkan key yang belum ada
    - Menyimpan hasil ke file
    """
    logger = setup_logger()

    env_path, key = resolve_env(env_input, env_dir)                 # Ambil path dan kunci
    lines = read_env_lines(env_path)                                # Baca isi file
    new_lines, found_keys = process_env_lines(lines, key)           # Enkripsi ulang key yang ditemukan
    updated_lines = add_missing_keys(new_lines, found_keys, key)    # Tambahkan key yang belum ada

    # Buat direktori jika belum tersedia
    os.makedirs(os.path.dirname(env_path), exist_ok = True)

    # Tulis ulang file dengan isi baru
    with open(env_path, "w") as f:
        f.writelines(updated_lines)

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        logger.info(f"[✓] File berhasil diperbarui → {env_path} \n")
