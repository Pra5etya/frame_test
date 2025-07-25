from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

import os, logging

def setup_logger():
    log_name = "record"
    log_dir = "logs"

    try:
        # Membuat direktori logs jika belum ada
        os.makedirs(log_dir, exist_ok = True)
        
        if os.path.exists(log_dir):
            print(f"Direktori '{log_dir}' berhasil dibuat atau sudah ada.")
        
        else:
            print(f"Direktori '{log_dir}' tidak berhasil dibuat.")
    
    except Exception as e:
        print(f"Gagal membuat direktori '{log_dir}': {e}")



    today_str = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/{log_name}_{today_str}.log"

    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Ganti ke TimedRotatingFileHandler (rotasi harian)
        handler = TimedRotatingFileHandler(
            filename = log_file,
            when = "midnight",          # Rotasi tiap tengah malam
            interval = 1,               # Setiap 1 hari
            backupCount = 30,           # Simpan 7 hari terakhir
            encoding = 'utf-8',
            utc = False                 # Rotasi berdasarkan waktu lokal
        )

        formatter = logging.Formatter("[%(asctime)s] \t %(levelname)s: \t %(message)s")
        handler.setFormatter(formatter)

        # Gunakan suffix agar nama file hasil rotasi konsisten
        handler.suffix = "%Y-%m-%d"

        logger.addHandler(handler)

    return logger