import hashlib
from database.db_manager import get_connection


def _md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def verify_login(username: str, password: str) -> bool:
    """Compare MD5(password) against officer.officer_login_password_md5."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT officer_login_name FROM officer "
            "WHERE officer_login_name = %s AND officer_login_password_md5 = %s",
            (username, _md5(password)),
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()
