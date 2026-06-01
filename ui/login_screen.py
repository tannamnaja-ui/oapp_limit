import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import COLORS, FONT


class LoginScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['light_blue'])
        self.app = app
        self._build()

    def _build(self):
        # ── Centre card ──────────────────────────────────────────────────
        card_wrap = tk.Frame(self, bg=COLORS['light_blue'])
        card_wrap.place(relx=0.5, rely=0.45, anchor='center')

        # Card header (dark blue banner)
        banner = tk.Frame(card_wrap, bg=COLORS['dark_blue'], padx=30, pady=14)
        banner.pack(fill='x')
        tk.Label(banner, text="ระบบจำกัดนัดคลินิก",
                 bg=COLORS['dark_blue'], fg='white',
                 font=(FONT, 16, 'bold')).pack()
        tk.Label(banner, text="Clinic Appointment Limit System",
                 bg=COLORS['dark_blue'], fg='#AED6F1',
                 font=(FONT, 9)).pack()

        # White form body
        body = tk.Frame(card_wrap, bg='white', padx=35, pady=25)
        body.pack(fill='x')

        def _row(r, lbl, var, show=''):
            tk.Label(body, text=lbl, bg='white',
                     font=(FONT, 10), width=10, anchor='e').grid(
                row=r, column=0, padx=(0, 8), pady=6)
            e = tk.Entry(body, textvariable=var, width=26,
                         font=(FONT, 10), relief='solid', bd=1, show=show)
            e.grid(row=r, column=1, pady=6)
            return e

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        user_entry = _row(0, "ชื่อผู้ใช้ :", self.username_var)
        pass_entry = _row(1, "รหัสผ่าน :", self.password_var, show='*')
        user_entry.focus_set()

        pass_entry.bind('<Return>', lambda _: self._login())

        # Login button
        tk.Button(body, text="เข้าสู่ระบบ",
                  bg=COLORS['medium_blue'], fg='white',
                  font=(FONT, 10, 'bold'), width=22,
                  relief='flat', cursor='hand2',
                  command=self._login).grid(row=2, column=0, columnspan=2,
                                            pady=(14, 4))

        ttk.Separator(body, orient='horizontal').grid(
            row=3, column=0, columnspan=2, sticky='ew', pady=8)

        # Connection settings link-button
        tk.Button(body, text="⚙  ตั้งค่าการเชื่อมต่อฐานข้อมูล",
                  bg='white', fg=COLORS['medium_blue'],
                  font=(FONT, 9), relief='flat', cursor='hand2',
                  command=lambda: self.app.show_connection('login')).grid(
            row=4, column=0, columnspan=2)

        # Status bar below card
        self._status_var = tk.StringVar()
        tk.Label(card_wrap, textvariable=self._status_var,
                 bg=COLORS['light_blue'], fg='#E74C3C',
                 font=(FONT, 9)).pack(pady=(4, 0))

    def _login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning("แจ้งเตือน",
                                   "กรุณากรอกชื่อผู้ใช้และรหัสผ่าน",
                                   parent=self)
            return

        self._status_var.set("กำลังตรวจสอบ...")
        self.update()

        try:
            from database.auth import verify_login
            if verify_login(username, password):
                self.app.current_user = username
                self.app.show_main()
            else:
                self._status_var.set("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
                messagebox.showerror("ล้มเหลว",
                                     "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง",
                                     parent=self)
        except Exception as exc:
            self._status_var.set("ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
            messagebox.showerror(
                "ข้อผิดพลาด",
                f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้\n"
                f"กรุณาตั้งค่าการเชื่อมต่อก่อน\n\n{exc}",
                parent=self)
