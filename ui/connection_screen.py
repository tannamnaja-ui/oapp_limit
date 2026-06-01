import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import COLORS, FONT
from config import load_config, save_config


# ── Per-database form widget ───────────────────────────────────────────────────
class _DBForm(tk.Frame):
    """Fields for one database type (MySQL or PostgreSQL)."""

    def __init__(self, parent, db_type: str):
        bg = COLORS['light_blue']
        super().__init__(parent, bg=bg, padx=18, pady=14)
        self.db_type = db_type
        default_port = '3300' if db_type == 'mysql' else '5432'

        self.vars: dict[str, tk.StringVar] = {}
        fields = [
            ('host',     'IP Server :',  '',           False),
            ('port',     'Port :',       default_port, False),
            ('database', 'Database :',   '',           False),
            ('username', 'Username :',   '',           False),
            ('password', 'Password :',   '',           True),
        ]
        for row, (key, label, default, masked) in enumerate(fields):
            tk.Label(self, text=label, bg=bg, font=(FONT, 10),
                     width=13, anchor='e').grid(
                row=row, column=0, padx=(0, 8), pady=6, sticky='e')
            var = tk.StringVar(value=default)
            self.vars[key] = var
            tk.Entry(self, textvariable=var, width=34, font=(FONT, 10),
                     relief='solid', bd=1,
                     show='*' if masked else '').grid(
                row=row, column=1, pady=6, sticky='w')
        self.columnconfigure(1, weight=1)

    def get_cfg(self) -> dict:
        return {
            'db_type':  self.db_type,
            'host':     self.vars['host'].get().strip(),
            'port':     self.vars['port'].get().strip(),
            'database': self.vars['database'].get().strip(),
            'username': self.vars['username'].get().strip(),
            'password': self.vars['password'].get(),
        }

    def load_from(self, data: dict):
        self.vars['host'].set(data.get('host', ''))
        self.vars['port'].set(str(data.get('port',
                                3300 if self.db_type == 'mysql' else 5432)))
        self.vars['database'].set(data.get('database', ''))
        self.vars['username'].set(data.get('username', ''))
        self.vars['password'].set(data.get('password', ''))


# ── Main connection screen ────────────────────────────────────────────────────
class ConnectionScreen(tk.Frame):
    def __init__(self, parent, app, from_screen='login'):
        super().__init__(parent, bg=COLORS['light_blue'])
        self.app = app
        self.from_screen = from_screen
        self._build()
        self._load()

    # ── Layout ────────────────────────────────────────────────────────────
    def _build(self):
        # Header bar
        hdr = tk.Frame(self, bg=COLORS['dark_blue'])
        hdr.pack(fill='x')
        tk.Label(hdr, text="ตั้งค่าการเชื่อมต่อฐานข้อมูล",
                 bg=COLORS['dark_blue'], fg='white',
                 font=(FONT, 12, 'bold')).pack(side='left', padx=12, pady=8)
        tk.Button(hdr, text="◀ กลับ",
                  bg=COLORS['dark_blue'], fg='#AED6F1',
                  font=(FONT, 9), relief='flat', cursor='hand2',
                  command=self._go_back).pack(side='right', padx=12, pady=8)

        body = tk.Frame(self, bg=COLORS['light_blue'])
        body.pack(fill='both', expand=True, padx=16, pady=12)

        # ── Left: active-selector + notebook ─────────────────────────────
        left = tk.Frame(body, bg=COLORS['light_blue'])
        left.pack(side='left', fill='both', expand=True, padx=(0, 12))

        # Active DB selector
        sel_lf = ttk.LabelFrame(left, text="ฐานข้อมูลที่ใช้งาน",
                                 style='Form.TLabelframe', padding=10)
        sel_lf.pack(fill='x', pady=(0, 10))

        self.active_var = tk.StringVar(value='mysql')
        for val, lbl, color in [
            ('mysql',      '● MySQL / MariaDB', '#1E6BB0'),
            ('postgresql', '● PostgreSQL',       '#336791'),
        ]:
            tk.Radiobutton(sel_lf, text=lbl, variable=self.active_var,
                           value=val, bg=COLORS['light_blue'],
                           fg=color, selectcolor=COLORS['light_blue'],
                           font=(FONT, 10, 'bold'),
                           activebackground=COLORS['light_blue'],
                           command=self._on_active_change).pack(
                side='left', padx=(0, 24))

        self._active_desc = tk.Label(sel_lf,
                                     text="",
                                     bg=COLORS['light_blue'],
                                     fg='#555555', font=(FONT, 8))
        self._active_desc.pack(side='left')

        # Notebook — one tab per DB
        self.nb = ttk.Notebook(left)
        self.nb.pack(fill='both', expand=True)

        self.mysql_form = _DBForm(self.nb, 'mysql')
        self.pg_form    = _DBForm(self.nb, 'postgresql')

        self.nb.add(self.mysql_form,    text="  MySQL / MariaDB  ")
        self.nb.add(self.pg_form,       text="  PostgreSQL  ")

        # Sync notebook tab with active radio when user clicks a tab
        self.nb.bind('<<NotebookTabChanged>>', self._on_tab_change)

        # ── Right: action buttons + status log ───────────────────────────
        right = tk.Frame(body, bg=COLORS['light_blue'], width=220)
        right.pack(side='right', fill='y')
        right.pack_propagate(False)

        actions = [
            ("🔌  ทดสอบการเชื่อมต่อ",   COLORS['medium_blue'], self._test),
            ("💾  บันทึกการตั้งค่า",      COLORS['medium_blue'], self._save),
            ("🏠  เปิดหน้าหลัก",          '#8E44AD',             self._open_main),
            ("✔  บันทึกและกลับ Login",    COLORS['green'],       self._save_and_back),
        ]
        for text, color, cmd in actions:
            tk.Button(right, text=text, bg=color, fg='white',
                      font=(FONT, 9), width=23, anchor='w', padx=8,
                      relief='flat', cursor='hand2',
                      command=cmd).pack(fill='x', pady=4)

        ttk.Separator(right, orient='horizontal').pack(fill='x', pady=8)

        tk.Label(right, text="สถานะการทดสอบ",
                 bg=COLORS['light_blue'], fg=COLORS['dark_blue'],
                 font=(FONT, 9, 'bold')).pack(anchor='w')

        self._log = tk.Text(right, height=12, font=(FONT, 9),
                            bg='white', relief='solid', bd=1,
                            state='disabled', wrap='word')
        self._log.pack(fill='both', expand=True, pady=(4, 0))

    # ── Sync helpers ──────────────────────────────────────────────────────
    def _on_active_change(self):
        tab_index = 0 if self.active_var.get() == 'mysql' else 1
        self.nb.select(tab_index)
        self._update_desc()

    def _on_tab_change(self, _event=None):
        idx = self.nb.index(self.nb.select())
        self.active_var.set('mysql' if idx == 0 else 'postgresql')
        self._update_desc()

    def _update_desc(self):
        names = {'mysql': 'MySQL / MariaDB', 'postgresql': 'PostgreSQL'}
        self._active_desc.config(
            text=f"← ใช้ {names[self.active_var.get()]} สำหรับ Login และการทำงาน")

    def _current_tab_form(self) -> _DBForm:
        return self.mysql_form if self.active_var.get() == 'mysql' else self.pg_form

    # ── Load / save config ────────────────────────────────────────────────
    def _load(self):
        cfg = load_config()
        self.active_var.set(cfg.get('active', 'mysql'))
        self.mysql_form.load_from(cfg.get('mysql', {}))
        self.pg_form.load_from(cfg.get('postgresql', {}))
        self._on_active_change()
        self._update_desc()

    def _build_full_config(self) -> dict:
        return {
            'active':     self.active_var.get(),
            'mysql':      {k: v for k, v in self.mysql_form.get_cfg().items()
                           if k != 'db_type'},
            'postgresql': {k: v for k, v in self.pg_form.get_cfg().items()
                           if k != 'db_type'},
        }

    # ── Log helper ─────────────────────────────────────────────────────────
    def _log_write(self, text: str, color: str = 'black'):
        self._log.config(state='normal')
        self._log.delete('1.0', tk.END)
        self._log.insert(tk.END, text)
        self._log.config(state='disabled', fg=color)

    def _go_back(self):
        self.app.show_main() if self.from_screen == 'main' else self.app.show_login()

    # ── Button actions ─────────────────────────────────────────────────────
    def _test(self):
        """Test whichever tab is currently visible."""
        form = self._current_tab_form()
        cfg  = form.get_cfg()
        if not cfg['host'] or not cfg['database']:
            messagebox.showwarning("แจ้งเตือน",
                                   "กรุณากรอก IP Server และ Database",
                                   parent=self)
            return
        db_name = 'MySQL' if cfg['db_type'] == 'mysql' else 'PostgreSQL'
        self._log_write(f"กำลังทดสอบ {db_name}...", '#2471A3')
        self.update()
        from database.db_manager import test_connection
        ok, msg = test_connection(cfg)
        self._log_write(
            f"[{db_name}]\n"
            f"{'✔ สำเร็จ' if ok else '✘ ล้มเหลว'}\n\n{msg}",
            COLORS['green'] if ok else COLORS['red'])

    def _save(self):
        cfg = self._build_full_config()
        save_config(cfg)
        self._log_write("บันทึกการตั้งค่าทั้งหมดเรียบร้อยแล้ว\n"
                        f"ใช้งาน: {cfg['active'].upper()}",
                        COLORS['green'])
        messagebox.showinfo("สำเร็จ",
                            "บันทึกการตั้งค่าการเชื่อมต่อเรียบร้อยแล้ว",
                            parent=self)

    def _open_main(self):
        self.app.show_main()

    def _save_and_back(self):
        cfg = self._build_full_config()
        save_config(cfg)
        active = cfg['active']
        db_cfg = cfg[active]
        msg = (
            f"บันทึกการตั้งค่าเรียบร้อยแล้ว\n\n"
            f"ใช้งาน    : {active.upper()}\n"
            f"Server   : {db_cfg['host']}:{db_cfg['port']}\n"
            f"Database : {db_cfg['database']}\n"
            f"Username : {db_cfg['username']}"
        )
        self.app.show_status(msg, callback=self.app.show_login)
