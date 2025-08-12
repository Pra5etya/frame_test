from config.logger import setup_logger
from script.generate_key import CURRENT_USER, ALLOWED_USERS

logger = setup_logger()

def iam_check():
    """
    Pastikan CURRENT_USER diizinkan untuk mengakses key management.
    """
    if CURRENT_USER not in ALLOWED_USERS:
        logger.warning(
            f"[SECURITY] Unauthorized access attempt by user '{CURRENT_USER}'. "
            f"Allowed users: {ALLOWED_USERS}"
        )
        raise PermissionError(f"User '{CURRENT_USER}' tidak diizinkan mengakses key management.")
