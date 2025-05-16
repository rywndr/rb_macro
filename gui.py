import tkinter as tk
from tkinter import ttk, font
from macro_logic import AntiAFKMacro

# define ui constants
APP_TITLE = "rb anti-afk"
WINDOW_SIZE = "360x320" # width x height
DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_INTERVAL_SECONDS = 5
INTERVAL_OPTIONS = [1, 2, 5, 10, 30, 60, 300]  # in seconds
PIXEL_OPTIONS = [1, 5, 10, 25, 50, 100]
DEFAULT_PIXELS = 50

class MacroUI:
    # init ui elements
    def __init__(self, master):
        # create macro logic instance first
        self.macro = AntiAFKMacro(status_callback=self.update_status_display, error_callback=self.update_status_display)

        master.title(APP_TITLE)
        master.geometry(WINDOW_SIZE)
        master.resizable(False, False)

        # store master for later use
        self.master = master
        self.macro.set_tk_master(master)

        # configure styles
        self._setup_styles()
        # now set root bg using style's bg color
        style = ttk.Style()
        master.configure(bg=style.lookup("Main.TFrame", "background"))


        # create main frame
        self.main_frame = ttk.Frame(master, padding="20 20 20 20", style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # create title
        title_label = ttk.Label(self.main_frame, text=APP_TITLE, style="Title.TLabel")
        title_label.pack(pady=(0, 15))

        # create controls frame
        controls_frame = ttk.Frame(self.main_frame, style="Controls.TFrame")
        controls_frame.pack(fill=tk.X, pady=(0,10))

        # interval dropdown
        ttk.Label(controls_frame, text="move every (secs):", style="Input.TLabel").grid(row=0, column=0, padx=(0,10), pady=5, sticky="w")
        self.interval_var = tk.IntVar(value=DEFAULT_INTERVAL_SECONDS)
        self.interval_dropdown = ttk.Combobox(controls_frame, textvariable=self.interval_var, values=INTERVAL_OPTIONS, width=8, style="Modern.TCombobox")
        self.interval_dropdown.grid(row=0, column=1, pady=5, sticky="ew")
        self.interval_dropdown.bind("<<ComboboxSelected>>", self.on_interval_change)
        self.macro.set_interval(DEFAULT_INTERVAL_SECONDS)

        # pixel move dropdown
        ttk.Label(controls_frame, text="move pixels by:", style="Input.TLabel").grid(row=1, column=0, padx=(0,10), pady=5, sticky="w")
        self.pixel_var = tk.IntVar(value=DEFAULT_PIXELS)
        self.pixel_dropdown = ttk.Combobox(controls_frame, textvariable=self.pixel_var, values=PIXEL_OPTIONS, width=8, style="Modern.TCombobox")
        self.pixel_dropdown.grid(row=1, column=1, pady=5, sticky="ew")
        self.pixel_dropdown.bind("<<ComboboxSelected>>", self.on_pixel_change)
        self.macro.set_move_pixels(DEFAULT_PIXELS)

        controls_frame.columnconfigure(1, weight=1)

        # create status display
        self.status_label = ttk.Label(self.main_frame, text="status: idle", style="Status.TLabel", anchor="center")
        self.status_label.pack(fill=tk.X, pady=(10,15))

        # create button frame for better layout control
        button_frame = ttk.Frame(self.main_frame, style="Controls.TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # create start button
        self.start_button = ttk.Button(button_frame, text="start", command=self.start_macro_ui, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, expand=True, padx=(0,5), fill=tk.X)

        # create stop button
        self.stop_button = ttk.Button(button_frame, text="stop", command=self.stop_macro_ui, style="Stop.TButton", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, expand=True, padx=(5,0), fill=tk.X)

        # set initial state for macro logic
        self.macro.stop() # ensure stopped initially

        # handle window close
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    # setup ui styles
    def _setup_styles(self):
        # define fonts
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)
        self.title_font = font.Font(family="Segoe UI Light", size=18)
        self.status_font = font.Font(family="Segoe UI Semibold", size=10)

        # define colors
        bg_color = "#2D2D2D"
        fg_color = "#CCCCCC"
        accent_color = "#007ACC"
        stop_color = "#C42B1C"
        disabled_fg_color = "#6A6A6A"
        entry_bg = "#3C3C3C"
        entry_fg = "#E0E0E0"

        style = ttk.Style()
        style.theme_use('clam')

        # frame styles
        style.configure("Main.TFrame", background=bg_color)
        style.configure("Controls.TFrame", background=bg_color)

        # label styles
        style.configure("TLabel", background=bg_color, foreground=fg_color, padding=5, font=self.default_font)
        style.configure("Title.TLabel", background=bg_color, foreground=accent_color, font=self.title_font, anchor="center")
        style.configure("Status.TLabel", background=bg_color, foreground=fg_color, font=self.status_font, padding=8)
        style.configure("Input.TLabel", background=bg_color, foreground=fg_color, font=self.default_font)

        # button styles
        style.configure("TButton", font=self.default_font, padding=(10, 8), relief=tk.FLAT, borderwidth=1)
        style.map("TButton",
            background=[('active', "#4A4A4A"), ('!disabled', "#3C3C3C")],
            foreground=[('!disabled', fg_color), ('disabled', disabled_fg_color)],
            relief=[('pressed', tk.SUNKEN), ('!pressed', tk.FLAT)])

        style.configure("Accent.TButton", background=accent_color, foreground="#FFFFFF")
        style.map("Accent.TButton",
            background=[('active', "#005A9E"), ('!disabled', accent_color)],
            relief=[('pressed', tk.SUNKEN), ('!pressed', tk.FLAT)])
        
        style.configure("Stop.TButton", background=stop_color, foreground="#FFFFFF")
        style.map("Stop.TButton",
            background=[('active', "#A32013"), ('!disabled', stop_color)],
            foreground=[('!disabled', "#FFFFFF"), ('disabled', disabled_fg_color)],
            relief=[('pressed', tk.SUNKEN), ('!pressed', tk.FLAT)])

        # combobox style
        style.configure("Modern.TCombobox", 
                        background=entry_bg, 
                        fieldbackground=entry_bg, 
                        foreground=entry_fg,
                        arrowcolor=fg_color,
                        selectbackground=entry_bg, # color of dropdown list bg
                        selectforeground=accent_color, # color of selected item text in dropdown
                        borderwidth=1,
                        relief=tk.FLAT,
                        padding=5)
        style.map("Modern.TCombobox",
                  fieldbackground=[('readonly', entry_bg)],
                  foreground=[('readonly', entry_fg)],
                  selectbackground=[('readonly', 'focus', accent_color)], # color when item in list is focused
                  selectforeground=[('readonly', 'focus', "#FFFFFF")])
        
        self.master.option_add('*TCombobox*Listbox.background', entry_bg)
        self.master.option_add('*TCombobox*Listbox.foreground', entry_fg)
        self.master.option_add('*TCombobox*Listbox.selectBackground', accent_color)
        self.master.option_add('*TCombobox*Listbox.selectForeground', "#FFFFFF")

    # handle interval change from ui
    def on_interval_change(self, event=None):
        selected_interval = self.interval_var.get()
        self.macro.set_interval(selected_interval)

    # handle pixel change from ui
    def on_pixel_change(self, event=None):
        selected_pixels = self.pixel_var.get()
        self.macro.set_move_pixels(selected_pixels)

    # start macro via ui
    def start_macro_ui(self):
        self.macro.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.interval_dropdown.config(state=tk.DISABLED)
        self.pixel_dropdown.config(state=tk.DISABLED)

    # stop macro via ui
    def stop_macro_ui(self):
        self.macro.stop()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.interval_dropdown.config(state=tk.NORMAL)
        self.pixel_dropdown.config(state=tk.NORMAL)

    # update status label text
    def update_status_display(self, message):
        self.status_label.config(text=f"status: {message}")

    # handle window close event
    def on_closing(self):
        self.macro.stop() # ensure macro stops
        self.master.destroy()