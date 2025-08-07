from dotenv import load_dotenv
from script.manage_env_key import update_env_file
import os, sys

# Mapping from CLI ke nama environment
ALIAS = {
    "development": ["d", "dev"],
    "staging": ["s", "stag"],
    "production": ["p", "pro", "prod"]
}

# Membalik alias menjadi mapping dari semua alias ke environment-nya
ALIAS_MAP = {alias: env for env, aliases in ALIAS.items() for alias in aliases}

def load_environment():
    # Step 1.1: Load .env utama
    load_dotenv()

    # Step 1.2: Dapatkan env dan direktori
    FLASK_ENV = os.getenv("FLASK_ENV", "")
    ENV_DIR = os.getenv("ENV_DIR", "")
    VALID_ENVS = set(os.getenv("VALID_ENVS", "").split(","))

    # Step 1.3: Load .env.<env> dengan override
    if FLASK_ENV:
        load_dotenv(f"{ENV_DIR}/.env.{FLASK_ENV}", override = True)

    return FLASK_ENV, ENV_DIR, VALID_ENVS

def get_CLI():
    FLASK_ENV, _, _ = load_environment()

    # Step 2: Ambil nilai environment dari CLI atau FLASK_ENV
    env_input = sys.argv[1].lower() if len(sys.argv) > 1 else FLASK_ENV.lower()

    # Step 3: Resolusi nama environment dari alias
    resolved_env = ALIAS_MAP.get(env_input, env_input)

    return resolved_env, env_input

def valid_and_update():
    resolved_env, env_input = get_CLI()
    _, ENV_DIR, VALID_ENVS = load_environment()

    # Step 4: Validasi environment
    if resolved_env not in VALID_ENVS:
        raise ValueError(f"Invalid environment '{env_input}' resolved to '{resolved_env}'. Allowed: {VALID_ENVS}")

    # Step 5: Pastikan file .env target tersedia
    update_env_file(resolved_env, ENV_DIR)

    # Step 6: Bangun path dan muat ulang file target
    env_path = os.path.join(ENV_DIR, f".env.{resolved_env}")
    
    if not os.path.isfile(env_path):
        raise FileNotFoundError(f"File environment tidak ditemukan: {env_path}")

    return resolved_env, env_path
