import tkinter as tk
from ui.styles import COLORS, FONT


class StatusScreen(tk.Frame):
    def __init__(self, parent, app, message: str = "", callback=None):
        super().__init__(parent, bg=COLORS['light_blue'])
        self.app = app
        self.callback = callback
        self._build(message)
        # Auto-navigate after 3 s
        self.after(3000, self._go)

    def _build(self, message: str):
        card = tk.Frame(self, bg='white', relief='solid', bd=1, padx=30, pady=25)
        card.place(relx=0.5, rely=0.45, anchor='center')

        # Green check circle
        circle = tk.Frame(card, bg=COLORS['green'], width=60, height=60)
        circle.pack()
        circle.pack_propagate(False)
        tk.Label(circle, text="✓", bg=COLORS['green'], fg='white',
                 font=(FONT, 26, 'bold')).place(relx=0.5, rely=0.5, anchor='center')

        tk.Label(card, text="บันทึกข้อมูลสำเร็จ!",
                 bg='white', fg=COLORS['dark_blue'],
                 font=(FONT, 14, 'bold')).pack(pady=(12, 8))

        tk.Label(card, text=message, bg='white', fg=COLORS['dark_text'],
                 font=(FONT, 10), justify='left').pack(pady=(0, 14))

        tk.Label(card, text="กำลังกลับไปหน้าเข้าสู่ระบบในอีก 3 วินาที...",
                 bg='white', fg='#888888', font=(FONT, 9)).pack()

        tk.Button(card, text="กลับหน้าเข้าสู่ระบบ",
                  bg=COLORS['medium_blue'], fg='white',
                  font=(FONT, 9), relief='flat', cursor='hand2',
                  command=self._go).pack(pady=(12, 0))

    def _go(self):
        if self.callback:
            self.callback()
