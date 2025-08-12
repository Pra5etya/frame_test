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
    # 
    load_dotenv()

    # 
    FLASK_ENV = os.getenv("FLASK_ENV", "")
    ENV_DIR = os.getenv("ENV_DIR", "")
    VALID_ENVS = set(os.getenv("VALID_ENVS", "").split(","))

    # 
    if FLASK_ENV:
        load_dotenv(f"{ENV_DIR}/.env.{FLASK_ENV}", override = True)

    return FLASK_ENV, ENV_DIR, VALID_ENVS

def get_CLI():
    # 
    FLASK_ENV, _, _ = load_environment()

    # 
    if len(sys.argv) > 1:
        env_input = sys.argv[1].lower()
        print(f'\nAmbil dari CLI: {env_input} \n')

    elif FLASK_ENV:
        env_input = FLASK_ENV.lower()
        print(f'\nAmbil dari ENV: {env_input}')
        
    else:
        env_input = "dev"  # ✅ default jika kosong semua
        print(f'\nAmbil dari default: {env_input}')

    # 
    resolved_env = ALIAS_MAP.get(env_input, env_input)

    return resolved_env, env_input


def valid_and_update():
    # 
    resolved_env, env_input = get_CLI()
    _, ENV_DIR, VALID_ENVS = load_environment()

    # 
    if resolved_env not in VALID_ENVS:
        raise ValueError(f"Invalid environment '{env_input}' resolved to '{resolved_env}'. Allowed: {VALID_ENVS}")

    # 
    update_env_file(resolved_env, ENV_DIR)

    # 
    env_path = os.path.join(ENV_DIR, f".env.{resolved_env}")
    
    if not os.path.isfile(env_path):
        raise FileNotFoundError(f"File environment tidak ditemukan: {env_path}")

    return resolved_env, env_path
