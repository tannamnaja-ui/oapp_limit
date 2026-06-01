import json
import os
import copy

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_config.json')

DEFAULT_CONFIG = {
    "active": "mysql",
    "mysql": {
        "host": "localhost",
        "port": 3300,
        "database": "",
        "username": "",
        "password": ""
    },
    "postgresql": {
        "host": "localhost",
        "port": 5432,
        "database": "",
        "username": "",
        "password": ""
    }
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # ── Migrate old flat format (db_type / host / port …) ──────────
            if 'mysql' not in data and 'postgresql' not in data:
                db_type = data.get('db_type', 'mysql')
                migrated = copy.deepcopy(DEFAULT_CONFIG)
                migrated['active'] = db_type
                migrated[db_type].update({
                    'host':     data.get('host', ''),
                    'port':     data.get('port', 3300 if db_type == 'mysql' else 5432),
                    'database': data.get('database', ''),
                    'username': data.get('username', ''),
                    'password': data.get('password', ''),
                })
                return migrated

            # ── Merge with defaults so missing keys are always present ──────
            cfg = copy.deepcopy(DEFAULT_CONFIG)
            cfg['active'] = data.get('active', cfg['active'])
            for db in ('mysql', 'postgresql'):
                if db in data:
                    cfg[db].update(data[db])
            return cfg

        except Exception:
            pass

    return copy.deepcopy(DEFAULT_CONFIG)


def save_config(config: dict) -> bool:
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return True


def get_active_db_config() -> dict:
    """Return the settings dict for the currently active DB, with db_type injected."""
    cfg = load_config()
    active = cfg.get('active', 'mysql')
    result = dict(cfg.get(active, {}))
    result['db_type'] = active
    return result
