from datetime import datetime
from config.logger import setup_logger
# from config.notifikasi import send_all_notifications

import os, shutil, subprocess

logger = setup_logger()

def backup_database(prefix: str):
    """
    Membackup database berdasarkan engine dari .env.
    Mendukung: SQLite, PostgreSQL, MySQL/MariaDB
    """

    engine = os.getenv(f"{prefix}_DB_ENGINE")
    db_name = os.getenv(f"{prefix}_DB_NAME")
    db_path = os.getenv(f"{prefix}_DB_PATH", "storage")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("backup", exist_ok=True)

    # === SQLite ===
    if engine == "sqlite":
        db_file = os.path.join(os.path.abspath(db_path), db_name)
        if not os.path.exists(db_file):
            logger.warning("SQLite DB file not found for backup.")
            return
        dest = os.path.join("backup", f"{prefix.lower()}_{timestamp}.db")
        shutil.copy2(db_file, dest)
        logger.info(f"[SQLite] Backup saved: {dest}")
        return

    # === PostgreSQL ===
    elif engine == "postgresql":
        user = os.getenv(f"{prefix}_DB_USERNAME")
        password = os.getenv(f"{prefix}_DB_PASSWORD")
        host = os.getenv(f"{prefix}_DB_HOST", "localhost")
        port = os.getenv(f"{prefix}_DB_PORT", "5432")
        os.environ["PGPASSWORD"] = password

        backup_file = os.path.join("backup", f"{prefix.lower()}_{timestamp}.sql")
        cmd = ["pg_dump", "-h", host, "-p", port, "-U", user, "-f", backup_file, db_name]

        try:
            subprocess.run(cmd, check=True)
            logger.info(f"[PostgreSQL] Backup saved: {backup_file}")
        except Exception as e:
            logger.error(f"[PostgreSQL] Backup failed: {e}")
        finally:
            os.environ.pop("PGPASSWORD", None)

    # === MySQL / MariaDB ===
    elif engine in ["mysql", "mariadb"]:
        user = os.getenv(f"{prefix}_DB_USERNAME")
        password = os.getenv(f"{prefix}_DB_PASSWORD")
        host = os.getenv(f"{prefix}_DB_HOST", "localhost")
        port = os.getenv(f"{prefix}_DB_PORT", "3306")

        backup_file = os.path.join("backup", f"{prefix.lower()}_{timestamp}.sql")
        cmd = ["mysqldump", "-h", host, "-P", port, "-u", user, f"-p{password}", db_name]

        try:
            with open(backup_file, "w") as f:
                subprocess.run(cmd, stdout=f, check=True)
            logger.info(f"[MySQL] Backup saved: {backup_file}")
        except Exception as e:
            logger.error(f"[MySQL] Backup failed: {e}")

    else:
        logger.warning(f"Backup not supported for engine: {engine}")

    # send_all_notifications(
    #     subject = f"Backup Sukses - {prefix}", 
    #     message = f"Database backup berhasil ({prefix}) pada {timestamp}"
    #     )