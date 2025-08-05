from config.env_set import (
    DevelopmentConfig,
    StagingConfig,
    ProductionConfig
)
from script.generate_key import update_env_file
from dotenv import load_dotenv

import os, sys


# Mapping alias CLI ke nama environment lengkap
ENV_ALIAS_MAP = {
    "dev": "development",
    "stag": "staging",
    "pro": "production"
}

CONFIG_MAP = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig
}

def load_root_env():
    root_env_path = os.path.join(os.getcwd(), ".env")
    load_dotenv(dotenv_path=root_env_path, override=False)

def resolve_env_name():
    # Ambil default dari .env atau kosong
    def_env = os.getenv("DEFAULT_ENV", "").lower()
    provider = os.getenv("SECRET_PROVIDER", "").lower()

    # Override kalau dari CLI ada
    if len(sys.argv) > 1:
        def_env = sys.argv[1]

    if len(sys.argv) > 2:
        provider = sys.argv[2].lower()

    # Validasi minimal
    if not def_env:
        raise ValueError("Environment name tidak ditemukan. Gunakan argumen CLI atau isi DEFAULT_ENV.")

    if ENV_ALIAS_MAP.get(def_env, def_env) == "production" and not provider:
        raise ValueError("Provider harus ditentukan di production. Gunakan: py run.py pro gcp")

    # Return mapped_env, raw_env, provider
    return ENV_ALIAS_MAP.get(def_env, def_env), def_env, provider


def get_env_settings():
    env_dir = os.getenv("ENV_DIR")
    valid_envs = set(os.getenv("VALID_ENVS").split(","))

    return env_dir, valid_envs

def load_target_env_file(env_dir, resolved_env):
    # Tambahkan pemanggilan untuk memastikan key dibuat (jika belum ada)
    update_env_file(resolved_env, env_dir)

    env_file_path = os.path.join(env_dir, f".env.{resolved_env}")

    if not os.path.exists(env_file_path):
        raise FileNotFoundError(f"Environment file not found: {env_file_path}")
    
    load_dotenv(dotenv_path=env_file_path, override=True)

    return env_file_path


def validate_env(resolved_env, valid_envs, original_env):
    if resolved_env not in valid_envs:
        raise ValueError(
            f"Invalid environment '{original_env}' resolved to '{resolved_env}'. Allowed: {valid_envs}"
        )

def load_env_files():
    # get root .env
    load_root_env()

    env_dir, valid_envs = get_env_settings()
    
    resolved_env, original_env, provider = resolve_env_name()

    print(f"Resolved env: {original_env} → Using .env.{resolved_env}")
    print(f"Provider: {provider}")
    
    env_file = load_target_env_file(env_dir, resolved_env)
    
    validate_env(resolved_env, valid_envs, original_env)
    
    os.environ["FLASK_ENV"] = resolved_env
    os.environ["SECRET_PROVIDER"] = provider  # ← Set global provider

    return resolved_env.lower(), env_file
