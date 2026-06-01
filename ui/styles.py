COLORS = {
    'dark_blue':    '#1B4F8A',
    'header_blue':  '#2B579A',
    'medium_blue':  '#4472C4',
    'light_blue':   '#D5E8F5',
    'panel_blue':   '#C8DFEF',
    'white':        '#FFFFFF',
    'dark_text':    '#1A1A2E',
    'green':        '#27AE60',
    'green_dark':   '#1E8449',
    'border':       '#B0C4D8',
    'toolbar':      '#A8C8E0',
    'red':          '#C0392B',
}

FONT = 'Tahoma'


def setup_styles(style):
    style.theme_use('clam')

    # ── Treeview ──────────────────────────────────────────────────────────
    style.configure('App.Treeview',
                    background='white', foreground=COLORS['dark_text'],
                    rowheight=24, fieldbackground='white', font=(FONT, 9))
    style.configure('App.Treeview.Heading',
                    background=COLORS['medium_blue'], foreground='white',
                    font=(FONT, 9, 'bold'), relief='flat', padding=(4, 4))
    style.map('App.Treeview.Heading',
              background=[('active', COLORS['dark_blue'])])
    style.map('App.Treeview',
              background=[('selected', COLORS['medium_blue'])],
              foreground=[('selected', 'white')])

    # ── Buttons ──────────────────────────────────────────────────────────
    for name, bg, active in [
        ('Blue',  COLORS['medium_blue'], COLORS['dark_blue']),
        ('Green', COLORS['green'],       COLORS['green_dark']),
        ('Red',   COLORS['red'],         '#922B21'),
        ('Gray',  '#7F8C8D',             '#566573'),
    ]:
        style.configure(f'{name}.TButton', background=bg, foreground='white',
                        font=(FONT, 9), padding=(8, 4), relief='flat')
        style.map(f'{name}.TButton',
                  background=[('active', active), ('pressed', active)])

    # ── Labels ───────────────────────────────────────────────────────────
    style.configure('Header.TLabel',
                    background=COLORS['header_blue'], foreground='white',
                    font=(FONT, 11, 'bold'))
    style.configure('Panel.TLabel',
                    background=COLORS['panel_blue'], foreground=COLORS['dark_text'],
                    font=(FONT, 9))
    style.configure('Form.TLabel',
                    background=COLORS['light_blue'], foreground=COLORS['dark_text'],
                    font=(FONT, 10))

    # ── Checkbutton / Radiobutton ────────────────────────────────────────
    for prefix, bg in [('Panel', COLORS['panel_blue']),
                       ('Form',  COLORS['light_blue'])]:
        style.configure(f'{prefix}.TCheckbutton',
                        background=bg, font=(FONT, 9))
        style.configure(f'{prefix}.TRadiobutton',
                        background=bg, font=(FONT, 9))

    # ── LabelFrame ───────────────────────────────────────────────────────
    style.configure('Panel.TLabelframe',
                    background=COLORS['panel_blue'])
    style.configure('Panel.TLabelframe.Label',
                    background=COLORS['panel_blue'],
                    foreground=COLORS['dark_blue'], font=(FONT, 9, 'bold'))
    style.configure('Form.TLabelframe',
                    background=COLORS['light_blue'])
    style.configure('Form.TLabelframe.Label',
                    background=COLORS['light_blue'],
                    foreground=COLORS['dark_blue'], font=(FONT, 9, 'bold'))
