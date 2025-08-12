# VENDOR SECRET MANAGER

## 🔐 Langkah 1: Buat Service Account Key
1. Buka Google Cloud Console - IAM & Admin > Service Accounts
2. Pilih project GCP kamu.
3. Klik "Create Service Account"
    1. Masukkan nama, misalnya: secretmanager-access
    2. Klik Continue
4. Pada bagian Grant this service account access to project, beri role:
    1. Secret Manager Secret Accessor
5. Klik Done
6. Klik service account yang baru → tab Keys
7. Klik "Add Key" > "Create new key" > JSON
8. Simpan file .json ke lokasi aman (misalnya: credentials/gcp-key.json)

## ⚙️ Langkah 2: Atur Environment Variable
```bash
# untuk secret manager
pip install google-cloud-secret-manager
```

### Opsi A – Sementara (via terminal)
```bash
# Windows
set GOOGLE_APPLICATION_CREDENTIALS=D:\GIT Data\frame_test\credentials\gcp-key.json

# Linux/macOS
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcp-key.json
```

### Opsi B – Permanen (via .env)
```env
GOOGLE_APPLICATION_CREDENTIALS=D:/GIT Data/frame_test/credentials/gcp-key.json
GCP_PROJECT_ID=your-project-id
GCP_SECRET_ID=your-secret-id
GCP_SECRET_VERSION=latest
```
Lalu muat .env di dalam Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

## 🧪 Contoh Fungsi load_gcp_secret_key
```python
import os
from google.cloud import secretmanager
from google.oauth2 import service_account
from dotenv import load_dotenv

def load_gcp_secret_key() -> bytes:
    load_dotenv()  # Memuat variabel dari .env

    project_id = os.getenv("GCP_PROJECT_ID")
    secret_id = os.getenv("GCP_SECRET_ID")
    version_id = os.getenv("GCP_SECRET_VERSION", "latest")
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Muat kredensial dari file JSON
    credentials = service_account.Credentials.from_service_account_file(cred_path)

    client = secretmanager.SecretManagerServiceClient(credentials=credentials)
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})

    return response.payload.data
```

## 📚 Referensi
* [Google Cloud Secret Manager Python Client](https://cloud.google.com/secret-manager/docs/reference/libraries)
* [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to)

# BUAT SENDIRI

| Fitur Secret Manager      | Bisa Dibuat Sendiri?  | Cara Implementasi                                              |
| ------------------------- | --------------------- | -------------------------------------------------------------- |
| 🔐 Enkripsi nilai secret  | ✅ Bisa                | Gunakan `cryptography.Fernet`, `AES-GCM`, atau `NaCl`          |
| 🧾 Versi secret           | ✅ Bisa manual         | Gunakan struktur folder + penamaan: `SECRET_NAME_v1.json`      |
| 🕓 Rotasi otomatis        | 🔶 Bisa semi-otomatis | Jadwalkan dengan cron job + CLI internal                       |
| 👥 Kontrol akses (IAM)    | 🔶 Bisa terbatas      | Buat user access rules berbasis per-folder atau file           |
| 📜 Audit log              | 🔶 Bisa manual        | Log akses secret ke file `access.log` secara programatik       |
| 🔁 Auto-load saat runtime | ✅ Bisa                | Tambahkan ke `create_app()` seperti yang sudah kamu lakukan    |
| ☁️ Penyimpanan cloud      | ✅ Bisa optional       | Gunakan GCS, S3, atau private Git repo bila mau remote storage |

## Hal yang harus di implementasi:
* Key Rotation with schedule dengan waktu 1 menit beserta thread process background
* IAM for user access
* Menerapkan key pool (min and max nya)
* Menerapkan grace period supaya key lama tidak langsung dibuang setelah rotasi.