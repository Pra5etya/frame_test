from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

# Step 1: Load .env utama
load_dotenv()

# Step 2: Dapatkan env dan direktori
env = os.getenv("FLASK_ENV") or "development"
ENV_DIR = os.getenv("ENV_DIR") or "environment"

# Step 3: Load .env.<env> dengan override
load_dotenv(f"{ENV_DIR}/.env.{env}", override=True)

# Step 4: Baru ambil variable yang dibutuhkan
INST_DIR = os.getenv("INST_DIR") 
LOCAL_KEY = os.getenv("LOCAL_KEY")
DEV_KEY = f"{INST_DIR}/{LOCAL_KEY}"


def encrypt_value(value: str, key: bytes) -> str:
    f = Fernet(key)
    token = f.encrypt(value.encode()).decode()
    return f"ENC({token})"

def load_master_key(env: str) -> bytes:
    if env == "development":
        return load_dev_key()
    
    elif env == "staging":
        return load_staging_key()
    
    elif env == "production":
        provider = os.getenv("SECRET_PROVIDER", "").lower()

        if provider == "gcp":
            print(f'Nama enkripsi provider yang digunakan: {provider}')
            # return load_gcp_secret_key()
        
        elif provider == "aws":
            print(f'Nama enkripsi provider yang digunakan: {provider}')
            # return load_aws_secret_key()
        
        else:
            raise ValueError("SECRET_PROVIDER (gcp/aws) tidak valid untuk production.")
    
    else:
        raise ValueError(f"Unknown environment: {env}")

def load_dev_key() -> bytes:
    with open(DEV_KEY, "rb") as f:
        return f.read()

def load_staging_key() -> bytes:
    return os.environ["APP_MASTER_KEY"].encode()

def load_gcp_secret_key() -> bytes:
    # must install pip install google-cloud-secret-manager
    from google.cloud import secretmanager

    project_id = os.getenv("GCP_PROJECT_ID")
    secret_id = os.getenv("GCP_SECRET_ID")
    version_id = os.getenv("GCP_SECRET_VERSION", "latest")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data

def load_aws_secret_key() -> bytes:
    import boto3
    from botocore.exceptions import ClientError

    secret_name = os.getenv("AWS_SECRET_NAME")
    region_name = os.getenv("AWS_REGION")

    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        return get_secret_value_response['SecretString'].encode()
    except ClientError as e:
        raise RuntimeError(f"AWS Secret fetch failed: {e}")
