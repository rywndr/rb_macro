import tkinter as tk
from gui import MacroUI

# main entry point
if __name__ == "__main__":
    # init main window
    root = tk.Tk()
    # create app instance
    app_ui = MacroUI(root)
    # start ui event loop
    root.mainloop()