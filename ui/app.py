import tkinter as tk
from tkinter import ttk
from ui.styles import setup_styles, COLORS, FONT


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("oapp_limit - ระบบจำกัดนัดคลินิก")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=COLORS['dark_blue'])

        # Center on screen
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = 1100, 720
        self.root.geometry(f'{w}x{h}+{(sw-w)//2}+{(sh-h)//2}')

        setup_styles(ttk.Style())

        self.current_user: str | None = None
        self._frame: tk.Widget | None = None

        self.container = tk.Frame(root)
        self.container.pack(fill='both', expand=True)

        self.show_login()

    # ── Navigation ────────────────────────────────────────────────────────
    def _switch(self, cls, **kw):
        if self._frame:
            self._frame.destroy()
        self._frame = cls(self.container, self, **kw)
        self._frame.pack(fill='both', expand=True)

    def show_login(self):
        from ui.login_screen import LoginScreen
        self._switch(LoginScreen)

    def show_connection(self, from_screen='login'):
        from ui.connection_screen import ConnectionScreen
        self._switch(ConnectionScreen, from_screen=from_screen)

    def show_main(self):
        from ui.main_screen import MainScreen
        self._switch(MainScreen)

    def show_status(self, message: str, callback):
        from ui.status_screen import StatusScreen
        self._switch(StatusScreen, message=message, callback=callback)
