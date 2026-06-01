import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime as _dt, date as _date, timedelta, time as _time
from flask import (Flask, render_template, request,
                   redirect, url_for, session, jsonify)

app = Flask(__name__)
app.secret_key = 'oapp_limit_s3cr3t_2025'


def _fmt_date(d):
    """Format oapp_date value as DD/MM/YYYY.
    รับได้ทั้ง string 'YYYY-MM-DD', datetime.date และ datetime.datetime"""
    if d is None:
        return ''
    if isinstance(d, str):
        # MySQL DATE_FORMAT คืน string 'YYYY-MM-DD' โดยตรง
        parts = d.split('-')
        if len(parts) == 3:
            return f"{parts[2]}/{parts[1]}/{parts[0]}"
        return d
    if isinstance(d, _dt):
        return d.date().strftime('%d/%m/%Y')
    if isinstance(d, _date):
        return d.strftime('%d/%m/%Y')
    try:
        return _dt.strptime(str(d).split()[0], '%Y-%m-%d').strftime('%d/%m/%Y')
    except Exception:
        return str(d)


def _fmt_time(t):
    """Format a MySQL TIME column (returned as timedelta) as HH:MM:SS."""
    if isinstance(t, timedelta):
        total = int(t.total_seconds())
        h, rem = divmod(total, 3600)
        m, s   = divmod(rem, 60)
        return f'{h:02d}:{m:02d}:{s:02d}'
    if isinstance(t, _time):
        return t.strftime('%H:%M:%S')
    return str(t) if t is not None else ''


# ── Index ──────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return redirect(url_for('main' if 'user' in session else 'login'))


# ── Login ──────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            from database.auth import verify_login
            if verify_login(username, password):
                session['user'] = username
                return redirect(url_for('main'))
            error = 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
        except Exception as exc:
            error = f'ไม่สามารถเชื่อมต่อฐานข้อมูลได้ — กรุณาตั้งค่าการเชื่อมต่อก่อน\n({exc})'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ── Connection settings ────────────────────────────────────────────────────────
@app.route('/connection', methods=['GET', 'POST'])
def connection():
    from config import load_config, save_config
    alert = None

    if request.method == 'POST':
        action = request.form.get('action', '')

        new_cfg = {
            'active': request.form.get('active', 'mysql'),
            'mysql': {
                'host':     request.form.get('mysql_host', '').strip(),
                'port':     request.form.get('mysql_port', '3300').strip(),
                'database': request.form.get('mysql_database', '').strip(),
                'username': request.form.get('mysql_username', '').strip(),
                'password': request.form.get('mysql_password', ''),
            },
            'postgresql': {
                'host':     request.form.get('pg_host', '').strip(),
                'port':     request.form.get('pg_port', '5432').strip(),
                'database': request.form.get('pg_database', '').strip(),
                'username': request.form.get('pg_username', '').strip(),
                'password': request.form.get('pg_password', ''),
            },
        }

        if action == 'test':
            active = new_cfg['active']
            test_cfg = dict(new_cfg[active])
            test_cfg['db_type'] = active
            from database.db_manager import test_connection
            ok, msg = test_connection(test_cfg)
            alert = {'type': 'success' if ok else 'danger',
                     'msg': f"[{active.upper()}] {'✔ ' if ok else '✘ '}{msg}"}

        elif action == 'save':
            save_config(new_cfg)
            alert = {'type': 'success', 'msg': 'บันทึกการตั้งค่าเรียบร้อยแล้ว'}

        elif action == 'open_main':
            save_config(new_cfg)
            return redirect(url_for('main'))

        elif action == 'save_back':
            save_config(new_cfg)
            active = new_cfg['active']
            db = new_cfg[active]
            return redirect(url_for('status',
                text=(f"บันทึกเรียบร้อยแล้ว\n"
                      f"ใช้งาน    : {active.upper()}\n"
                      f"Server   : {db['host']}:{db['port']}\n"
                      f"Database : {db['database']}\n"
                      f"Username : {db['username']}")))

        return render_template('connection.html', cfg=new_cfg, alert=alert)

    cfg = load_config()
    return render_template('connection.html', cfg=cfg, alert=alert)


# ── Main screen ────────────────────────────────────────────────────────────────
@app.route('/main')
def main():
    if 'user' not in session:
        return redirect(url_for('login'))

    clinics  = []
    db_error = None

    try:
        from database.db_manager import execute_query
        try:
            clinics = execute_query(
                "SELECT clinic_code, clinic_name FROM clinic ORDER BY clinic_name")
        except Exception:
            pass
    except Exception as exc:
        db_error = str(exc)

    return render_template('main.html',
                           user=session['user'],
                           clinics=clinics,
                           db_error=db_error)


# ── API: records list ─────────────────────────────────────────────────────────
@app.route('/api/records')
def api_records():
    if 'user' not in session:
        return jsonify({'ok': False, 'msg': 'Unauthorized'}), 401

    start  = request.args.get('start',  '').strip()   # YYYY-MM-DD
    end    = request.args.get('end',    '').strip()   # YYYY-MM-DD
    clinic = request.args.get('clinic', '').strip()   # e.g. '003'

    if not start or not end:
        return jsonify({'ok': True, 'records': []})

    result = []
    try:
        from database.db_manager import execute_query

        sql = ("SELECT DATE(oapp_date) AS oapp_date, oapp_clinic, oapp_limit, "
               "       start_time, end_time, check_time, limit_note "
               "FROM   oapp_limit "
               "WHERE  DATE(oapp_date) BETWEEN %s AND %s ")
        params = [start, end]

        if clinic:
            sql += "AND oapp_clinic = %s "
            params.append(clinic)

        sql += "ORDER BY oapp_date, start_time LIMIT 200"

        rows = execute_query(sql, params=tuple(params))

        for i, r in enumerate(rows, 1):
            result.append({
                'no':         i,
                'date':       _fmt_date(r[0]),
                'clinic':     str(r[1]) if r[1] is not None else '',
                'limit':      str(r[2]) if r[2] is not None else '',
                'start_time': _fmt_time(r[3]),
                'end_time':   _fmt_time(r[4]),
                'check_time': str(r[5]) if r[5] is not None else '',
                'note':       str(r[6]) if r[6] is not None else '',
            })
    except Exception as exc:
        return jsonify({'ok': False, 'msg': str(exc)}), 500

    return jsonify({'ok': True, 'records': result})


# ── API: debug date (ชั่วคราว) ────────────────────────────────────────────────
@app.route('/api/debug-date')
def api_debug_date():
    if 'user' not in session:
        return jsonify({'error': 'not logged in'}), 401
    try:
        from database.db_manager import execute_query
        rows = execute_query(
            "SELECT oapp_date, DATE(oapp_date) AS date_only "
            "FROM oapp_limit ORDER BY oapp_date LIMIT 3"
        )
        out = []
        for r in rows:
            out.append({
                'raw_oapp_date':       str(r[0]),
                'raw_oapp_date_type':  type(r[0]).__name__,
                'date_only':           str(r[1]),
                'date_only_type':      type(r[1]).__name__,
                '_fmt_date_result':    _fmt_date(r[1]),
            })
        return jsonify(out)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


# ── API: create records ────────────────────────────────────────────────────────
@app.route('/api/create-records', methods=['POST'])
def api_create_records():
    if 'user' not in session:
        return jsonify({'ok': False, 'msg': 'Unauthorized'}), 401
    # TODO: implement actual DB insert logic
    return jsonify({'ok': True, 'msg': 'สร้างรายการเรียบร้อยแล้ว'})


# ── Status page ────────────────────────────────────────────────────────────────
@app.route('/status')
def status():
    text = request.args.get('text', 'บันทึกเรียบร้อยแล้ว')
    return render_template('status.html', text=text)


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3300))
    print(f"\n  oapp_limit กำลังทำงานที่  http://localhost:{port}\n")
    app.run(debug=True, port=port, host='0.0.0.0')
