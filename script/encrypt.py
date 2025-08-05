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
    if key is None:
        raise ValueError("Encryption key is None. Make sure the key is loaded properly.")

    else: 
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
            return load_gcp_secret_key()
        
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

    if not all([project_id, secret_id]):
        raise EnvironmentError("GCP_PROJECT_ID dan GCP_SECRET_ID harus diset di environment.")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    
    try:
        response = client.access_secret_version(request={"name": name})
        secret_data = response.payload.data  # type: bytes

    except Exception as e:
        raise RuntimeError(f"Gagal mengakses secret dari GCP: {e}")

    if not secret_data:
        raise ValueError("Key tidak berhasil dimuat. Secret kosong atau tidak valid.")

    return secret_data


def load_aws_secret_key() -> bytes:
    import boto3
    from botocore.exceptions import ClientError

    secret_name = os.getenv("AWS_SECRET_NAME")
    region_name = os.getenv("AWS_REGION")

    if not all([secret_name, region_name]):
        raise EnvironmentError("AWS_SECRET_NAME dan AWS_REGION harus diset di environment.")

    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)

        # Secret bisa berada di SecretString atau SecretBinary
        if 'SecretString' in response:
            secret_data = response['SecretString'].encode()

        elif 'SecretBinary' in response:
            secret_data = response['SecretBinary']
            
        else:
            raise ValueError("Secret tidak ditemukan dalam SecretString maupun SecretBinary.")

        if not secret_data:
            raise ValueError("Secret kosong. Pastikan secret AWS berisi data yang valid.")

        return secret_data

    except ClientError as e:
        raise RuntimeError(f"Gagal mengambil secret dari AWS Secrets Manager: {e}")

