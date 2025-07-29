from app import create_app
import os

app = create_app()

# # Load environment terenkripsi
# load_encrypted_env(ENV)

if __name__ == "__main__":
    # print(f'Start Application: {os.environ["FLASK_ENV"]} \n')     # Hanya untuk testing, jika sudah hapus kembali !!!
    # time.sleep(3)                                                 # Hanya untuk testing, jika sudah hapus kembali !!!

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

    print(f'\n')

    for key in flask_env_keys:
        value = os.environ.get(key)
        if value is not None:
            print(f"{key} = {value}")

    print(f'\n')

    

    app.run(debug = True)