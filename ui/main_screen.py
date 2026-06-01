import tkinter as tk
from tkinter import ttk, messagebox
from ui.styles import COLORS, FONT


class MainScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=COLORS['panel_blue'])
        self.app = app
        self._build()
        self._load_clinics()

    # ── Top bar ───────────────────────────────────────────────────────────
    def _build(self):
        hdr = tk.Frame(self, bg=COLORS['dark_blue'])
        hdr.pack(fill='x')
        tk.Label(hdr, text="ระบบจำกัดนัดคลินิก",
                 bg=COLORS['dark_blue'], fg='white',
                 font=(FONT, 11, 'bold')).pack(side='left', padx=10, pady=6)
        tk.Button(hdr, text="ออกจากระบบ",
                  bg=COLORS['red'], fg='white',
                  font=(FONT, 9), relief='flat', cursor='hand2',
                  command=self.app.show_login).pack(side='right', padx=6, pady=5)
        tk.Button(hdr, text="⚙ ตั้งค่าการเชื่อมต่อ",
                  bg=COLORS['medium_blue'], fg='white',
                  font=(FONT, 9), relief='flat', cursor='hand2',
                  command=lambda: self.app.show_connection('main')).pack(
            side='right', padx=(0, 4), pady=5)

        # ── Two-pane body ─────────────────────────────────────────────────
        body = tk.Frame(self, bg=COLORS['panel_blue'])
        body.pack(fill='both', expand=True)

        self._build_left(body)

        ttk.Separator(body, orient='vertical').pack(side='left', fill='y')

        self._build_right(body)

    # ── Left pane (list) ──────────────────────────────────────────────────
    def _build_left(self, parent):
        left = tk.Frame(parent, bg=COLORS['panel_blue'], width=330)
        left.pack(side='left', fill='both')
        left.pack_propagate(False)

        # Toolbar packed first so it anchors to bottom
        tb = tk.Frame(left, bg=COLORS['toolbar'], relief='raised', bd=1)
        tb.pack(side='bottom', fill='x')
        self._fill_toolbar(tb, [
            ('|◄', self._list_first),
            ('◄',  self._list_prev),
            ('►',  self._list_next),
            ('►|', self._list_last),
            ('+',  lambda: None),
            ('−',  self._delete_selected),
            ('✎',  lambda: None),
        ])

        # Treeview
        tree_f = tk.Frame(left, bg=COLORS['panel_blue'])
        tree_f.pack(fill='both', expand=True)

        self.list_tree = ttk.Treeview(
            tree_f,
            columns=('no', 'date', 'day', 'timerange'),
            show='headings',
            style='App.Treeview',
            selectmode='browse',
        )
        for col, lbl, w in [
            ('no',        'ลำดับ',    50),
            ('date',      'วันที่',    95),
            ('day',       'วัน',       70),
            ('timerange', 'ช่วงเวลา', 100),
        ]:
            self.list_tree.heading(col, text=lbl)
            self.list_tree.column(col, width=w, minwidth=w, anchor='center')

        vsb = ttk.Scrollbar(tree_f, orient='vertical',
                            command=self.list_tree.yview)
        self.list_tree.configure(yscrollcommand=vsb.set)
        self.list_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        # "No data" placeholder
        self._no_data_lbl = tk.Label(
            tree_f, text="<No data to display>",
            bg='white', fg='#999999', font=(FONT, 9))

    # ── Right pane (form) ─────────────────────────────────────────────────
    def _build_right(self, parent):
        right = tk.Frame(parent, bg=COLORS['panel_blue'])
        right.pack(side='right', fill='both', expand=True)

        # Toolbar at bottom
        tb = tk.Frame(right, bg=COLORS['toolbar'], relief='raised', bd=1)
        tb.pack(side='bottom', fill='x')
        self._fill_toolbar(tb, [
            ('|◄', lambda: None),
            ('◄',  lambda: None),
            ('►',  lambda: None),
            ('►|', lambda: None),
            ('+',  self._clear_form),
            ('−',  lambda: None),
            ('💾', self._save_data),
        ])

        # Panel header
        ph = tk.Frame(right, bg=COLORS['dark_blue'])
        ph.pack(fill='x')
        tk.Label(ph, text="กำหนดการจำกัดนัดตามช่วงเวลา",
                 bg=COLORS['dark_blue'], fg='white',
                 font=(FONT, 10, 'bold')).pack(side='left', padx=10, pady=5)
        tk.Button(ph, text="▶ สร้างรายการ",
                  bg=COLORS['green'], fg='white',
                  font=(FONT, 9, 'bold'), relief='flat', cursor='hand2',
                  command=self._create_records).pack(side='right', padx=8, pady=4)

        # Scrollable form area
        canvas = tk.Canvas(right, bg=COLORS['panel_blue'],
                           highlightthickness=0)
        sc_vsb = ttk.Scrollbar(right, orient='vertical',
                                command=canvas.yview)
        canvas.configure(yscrollcommand=sc_vsb.set)
        sc_vsb.pack(side='right', fill='y')
        canvas.pack(fill='both', expand=True)

        form_wrap = tk.Frame(canvas, bg=COLORS['panel_blue'])
        canvas_win = canvas.create_window((0, 0), window=form_wrap,
                                           anchor='nw')

        def _resize(event):
            canvas.itemconfig(canvas_win, width=event.width)
        canvas.bind('<Configure>', _resize)
        form_wrap.bind('<Configure>',
                       lambda e: canvas.configure(
                           scrollregion=canvas.bbox('all')))

        self._build_form(form_wrap)

    def _build_form(self, parent):
        # ── ข้อมูลการจำกัด section ───────────────────────────────────────
        sec = ttk.LabelFrame(parent, text="ข้อมูลการจำกัด",
                              style='Panel.TLabelframe', padding=10)
        sec.pack(fill='x', padx=8, pady=(8, 4))

        def _lbl(frame, text, row, col, **kw):
            tk.Label(frame, text=text, bg=COLORS['panel_blue'],
                     font=(FONT, 9), **kw).grid(
                row=row, column=col, sticky='e', padx=(0, 6), pady=3)

        def _entry(frame, var, row, col, width=38, show=''):
            e = tk.Entry(frame, textvariable=var, width=width,
                         font=(FONT, 9), relief='solid', bd=1, show=show)
            e.grid(row=row, column=col, sticky='w', pady=3)
            return e

        # Reference / search field (top of section, matches screenshot)
        self.ref_var = tk.StringVar()
        tk.Entry(sec, textvariable=self.ref_var, width=40,
                 font=(FONT, 9), relief='solid', bd=1).grid(
            row=0, column=0, columnspan=4, sticky='ew', pady=(0, 6))

        # คลินิก
        _lbl(sec, "คลินิก", 1, 0)
        self.clinic_var = tk.StringVar()
        self.clinic_cb = ttk.Combobox(sec, textvariable=self.clinic_var,
                                       width=40, font=(FONT, 9),
                                       state='readonly')
        self.clinic_cb.grid(row=1, column=1, columnspan=3,
                            sticky='w', pady=3)

        # วันที่เริ่มต้น / ถึงวันที่  (simple text entries with dd/mm/yyyy hint)
        _lbl(sec, "วันที่เริ่มต้น", 2, 0)
        date_row = tk.Frame(sec, bg=COLORS['panel_blue'])
        date_row.grid(row=2, column=1, columnspan=3, sticky='w', pady=3)
        self.start_date_var = tk.StringVar()
        self.end_date_var   = tk.StringVar()
        tk.Entry(date_row, textvariable=self.start_date_var, width=14,
                 font=(FONT, 9), relief='solid', bd=1).pack(side='left')
        tk.Label(date_row, text="ถึงวันที่", bg=COLORS['panel_blue'],
                 font=(FONT, 9)).pack(side='left', padx=(10, 6))
        tk.Entry(date_row, textvariable=self.end_date_var, width=14,
                 font=(FONT, 9), relief='solid', bd=1).pack(side='left')
        tk.Label(date_row, text="(วว/ดด/ปปปป)",
                 bg=COLORS['panel_blue'], fg='#888888',
                 font=(FONT, 8)).pack(side='left', padx=(6, 0))

        # สัปดาห์ที่ + ไม่สร้าง Slot วันหยุด
        _lbl(sec, "สัปดาห์ที่", 3, 0)
        week_row = tk.Frame(sec, bg=COLORS['panel_blue'])
        week_row.grid(row=3, column=1, columnspan=3, sticky='w', pady=3)
        self.week_var = tk.StringVar(value='None selected')
        self.week_cb = ttk.Combobox(week_row, textvariable=self.week_var,
                                     width=22, font=(FONT, 9))
        self.week_cb['values'] = ['None selected', '1', '2', '3', '4', '5']
        self.week_cb.pack(side='left')
        self.no_holiday_var = tk.BooleanVar()
        tk.Checkbutton(week_row, text="ไม่สร้าง Slot วันหยุด",
                       variable=self.no_holiday_var,
                       bg=COLORS['panel_blue'],
                       font=(FONT, 9)).pack(side='left', padx=(12, 0))

        # วัน checkboxes
        day_lf = ttk.LabelFrame(sec, text="วัน",
                                  style='Panel.TLabelframe', padding=6)
        day_lf.grid(row=4, column=0, columnspan=4,
                    sticky='ew', pady=(5, 3), padx=(0, 4))
        self.day_vars = {}
        day_layout = [
            ('จันทร์',   'mon', 0, 0, True),
            ('อังคาร',   'tue', 1, 0, True),
            ('พุธ',      'wed', 2, 0, True),
            ('พฤหัสบดี', 'thu', 3, 0, True),
            ('ศุกร์',    'fri', 4, 0, True),
            ('เสาร์',    'sat', 0, 1, False),
            ('อาทิตย์',  'sun', 1, 1, False),
        ]
        for lbl, key, r, c, default in day_layout:
            var = tk.BooleanVar(value=default)
            self.day_vars[key] = var
            tk.Checkbutton(day_lf, text=lbl, variable=var,
                           bg=COLORS['panel_blue'],
                           font=(FONT, 9)).grid(
                row=r, column=c, sticky='w', padx=(8, 30), pady=1)

        # Slot limit amount
        limit_row = tk.Frame(sec, bg=COLORS['panel_blue'])
        limit_row.grid(row=6, column=0, columnspan=4,
                       sticky='ew', pady=3)
        tk.Label(limit_row, text="จำนวนจำกัด :", bg=COLORS['panel_blue'],
                 font=(FONT, 9)).pack(side='left', padx=(0, 6))
        self.limit_var = tk.StringVar()
        tk.Entry(limit_row, textvariable=self.limit_var, width=10,
                 font=(FONT, 9), relief='solid', bd=1).pack(side='left')
        tk.Label(limit_row, text="ราย / slot", bg=COLORS['panel_blue'],
                 font=(FONT, 9)).pack(side='left', padx=(6, 0))

        sec.columnconfigure(1, weight=1)

        # ── หมายเหตุ ──────────────────────────────────────────────────────
        note_lf = ttk.LabelFrame(parent, text="หมายเหตุ",
                                  style='Panel.TLabelframe', padding=6)
        note_lf.pack(fill='x', padx=8, pady=(4, 4))
        self.note_text = tk.Text(note_lf, height=4, font=(FONT, 9),
                                  relief='solid', bd=1, wrap='word')
        note_vsb = ttk.Scrollbar(note_lf, orient='vertical',
                                  command=self.note_text.yview)
        self.note_text.configure(yscrollcommand=note_vsb.set)
        note_vsb.pack(side='right', fill='y')
        self.note_text.pack(side='left', fill='both', expand=True)

        # ── Slot detail grid (bottom of right panel) ──────────────────────
        slot_lf = ttk.LabelFrame(parent, text="รายการ Slot",
                                  style='Panel.TLabelframe', padding=4)
        slot_lf.pack(fill='both', expand=True, padx=8, pady=(4, 8))

        self.slot_tree = ttk.Treeview(
            slot_lf,
            columns=('time', 'limit', 'note'),
            show='headings',
            style='App.Treeview',
            height=6,
        )
        for col, lbl, w in [
            ('time',  'ช่วงเวลา',   160),
            ('limit', 'จำนวนจำกัด', 110),
            ('note',  'หมายเหตุ',   220),
        ]:
            self.slot_tree.heading(col, text=lbl)
            self.slot_tree.column(col, width=w, anchor='center')

        slot_vsb = ttk.Scrollbar(slot_lf, orient='vertical',
                                  command=self.slot_tree.yview)
        self.slot_tree.configure(yscrollcommand=slot_vsb.set)
        slot_vsb.pack(side='right', fill='y')
        self.slot_tree.pack(side='left', fill='both', expand=True)

    # ── Toolbar helper ─────────────────────────────────────────────────────
    @staticmethod
    def _fill_toolbar(frame, buttons):
        for text, cmd in buttons:
            tk.Button(frame, text=text, command=cmd,
                      bg=COLORS['toolbar'], relief='flat',
                      font=(FONT, 9), width=3,
                      cursor='hand2').pack(side='left', padx=1, pady=2)
        ttk.Separator(frame, orient='vertical').pack(
            side='left', fill='y', padx=3, pady=2)

    # ── Data loading ───────────────────────────────────────────────────────
    def _load_clinics(self):
        try:
            from database.db_manager import execute_query
            rows = execute_query(
                "SELECT clinic_code, clinic_name FROM clinic ORDER BY clinic_name"
            )
            self.clinic_cb['values'] = [f"{r[0]} - {r[1]}" for r in rows]
        except Exception:
            self.clinic_cb['values'] = []

    # ── Actions ────────────────────────────────────────────────────────────
    def _create_records(self):
        clinic = self.clinic_var.get().strip()
        start  = self.start_date_var.get().strip()
        end    = self.end_date_var.get().strip()

        if not clinic:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกคลินิก",
                                   parent=self)
            return
        if not start or not end:
            messagebox.showwarning("แจ้งเตือน",
                                   "กรุณาระบุวันที่เริ่มต้นและสิ้นสุด",
                                   parent=self)
            return
        selected = [k for k, v in self.day_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("แจ้งเตือน",
                                   "กรุณาเลือกอย่างน้อย 1 วัน",
                                   parent=self)
            return

        # TODO: implement DB insert and populate list_tree
        messagebox.showinfo("สำเร็จ",
                            "สร้างรายการเรียบร้อยแล้ว",
                            parent=self)

    def _delete_selected(self):
        sel = self.list_tree.selection()
        if not sel:
            messagebox.showwarning("แจ้งเตือน",
                                   "กรุณาเลือกรายการที่ต้องการลบ",
                                   parent=self)
            return
        if messagebox.askyesno("ยืนยัน",
                                "ต้องการลบรายการที่เลือกหรือไม่?",
                                parent=self):
            for item in sel:
                self.list_tree.delete(item)

    def _clear_form(self):
        self.ref_var.set('')
        self.clinic_var.set('')
        self.start_date_var.set('')
        self.end_date_var.set('')
        self.week_var.set('None selected')
        self.no_holiday_var.set(False)
        self.limit_var.set('')
        for key, var in self.day_vars.items():
            var.set(key not in ('sat', 'sun'))
        self.note_text.delete('1.0', tk.END)
        for item in self.slot_tree.get_children():
            self.slot_tree.delete(item)

    def _save_data(self):
        # TODO: implement DB save
        messagebox.showinfo("สำเร็จ", "บันทึกข้อมูลเรียบร้อยแล้ว",
                            parent=self)

    # ── List navigation stubs ──────────────────────────────────────────────
    def _list_first(self):
        children = self.list_tree.get_children()
        if children:
            self.list_tree.selection_set(children[0])
            self.list_tree.see(children[0])

    def _list_last(self):
        children = self.list_tree.get_children()
        if children:
            self.list_tree.selection_set(children[-1])
            self.list_tree.see(children[-1])

    def _list_prev(self):
        sel = self.list_tree.selection()
        if sel:
            prev_item = self.list_tree.prev(sel[0])
            if prev_item:
                self.list_tree.selection_set(prev_item)
                self.list_tree.see(prev_item)

    def _list_next(self):
        sel = self.list_tree.selection()
        if sel:
            next_item = self.list_tree.next(sel[0])
            if next_item:
                self.list_tree.selection_set(next_item)
                self.list_tree.see(next_item)
