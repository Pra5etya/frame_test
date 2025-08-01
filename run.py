from app import create_app
import os

app = create_app()

# # Load environment terenkripsi
# load_encrypted_env(ENV)

if __name__ == "__main__":
    # # cek semua nilai environ per-baris
    # for key, value in os.environ.items():
    #     if 'SECRET' in key.upper() or 'SECRET' in value.upper():
    #         print(f"{key} = {value}  # <-- contains SECRET")
        
    #     else:
    #         print(f"{key} = {value}")


    # Daftar environment penting yang biasa digunakan dalam proyek Flask
    flask_env_keys = {
        # default flask
        'DEFAULT_ENV', 
        'DEFAULT_HOST', 
        'DEFAULT_PORT', 

        # directory
        'INST_DIR', 
        'ENV_DIR', 

        # environment
        'VALID_ENVS', 

        # ENVIRONMENT
        'FLASK_ENV', 
        'DEBUG', 

        # SECRET KEY
        'SECRET_KEY', 
        'JWT_KEY', 
        'CSRF_KEY', 
        'SECRET_PROVIDER', 

        # DATABASE
        'DB_ENGINE', 
        'DB_DRIVER', 
        'DB_USERNAME', 
        'DB_PASSWORD', 
        'DB_HOST', 
        'DB_PORT', 
        'DB_NAME', 
        'DB_PATH', 
    }

    # print(f'\n')

    # for key in flask_env_keys:
    #     value = os.environ.get(key)
    #     if value is not None:
    #         print(f"{key} = {value}")

    # print(f'\n')

    # Testing Environment Key Value
    from script.manage_key import print_master_key

    # print_master_key("development") # kunci dibuat ketika .masterkey tidak ada filenya
    # print_master_key("staging") # kunci dibuat ketika runtime di jalankan (setiap kali run aplikasi) dan tidak disimpan pada .env.stag
    print_master_key("production")  # kunci untuk production dimana disimpan terpisah di luar aplikasi utama atau root project

    app.run(debug = True)