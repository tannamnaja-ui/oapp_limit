import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import get_active_db_config


def _make_connection(cfg: dict):
    """Open and return a raw DB connection from a settings dict."""
    db_type = cfg.get('db_type', 'mysql')
    host     = cfg.get('host', 'localhost')
    port     = int(cfg.get('port', 3300 if db_type == 'mysql' else 5432))
    database = cfg.get('database', '')
    username = cfg.get('username', '')
    password = cfg.get('password', '')

    if db_type == 'mysql':
        import mysql.connector
        return mysql.connector.connect(
            host=host, port=port, database=database,
            user=username, password=password,
            charset='utf8mb4', connect_timeout=10,
        )
    if db_type == 'postgresql':
        import psycopg2
        return psycopg2.connect(
            host=host, port=port, dbname=database,
            user=username, password=password,
            connect_timeout=10,
        )
    raise ValueError(f"Unsupported db_type: {db_type}")


def get_connection():
    """Open a connection using the currently active DB settings."""
    return _make_connection(get_active_db_config())


def test_connection(cfg: dict) -> tuple[bool, str]:
    """Test a connection from any settings dict (not necessarily the active one)."""
    try:
        conn = _make_connection(cfg)
        conn.close()
        return True, "เชื่อมต่อสำเร็จ!"
    except Exception as exc:
        return False, str(exc)


def execute_query(query: str, params=None, fetch: bool = True):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        conn.commit()
        cursor.close()
    finally:
        conn.close()
