import pydirectinput
import time
import pygetwindow

# define default constants
DEFAULT_MOUSE_MOVE_PIXELS = 50

class AntiAFKMacro:
    # init macro instance
    def __init__(self, status_callback, error_callback):
        self.is_running = False
        self.after_id = None
        self.move_interval_ms = 5 * 1000  # default to 5 secs
        self.mouse_move_pixels = DEFAULT_MOUSE_MOVE_PIXELS
        self.status_update_callback = status_callback # func to call for status updates
        self.error_update_callback = error_callback # func to call for error updates
        self.tk_master = None # placeholder for tkinter master if needed for .after()

    # set tk master for .after()
    def set_tk_master(self, master):
        self.tk_master = master

    # set movement interval
    def set_interval(self, interval_seconds):
        self.move_interval_ms = int(interval_seconds * 1000)
        print(f"interval set to {interval_seconds}s")

    # set move pixels
    def set_move_pixels(self, pixels):
        self.mouse_move_pixels = pixels
        print(f"move pixels set to {pixels}px")

    # start macro ops
    def start(self):
        if not self.tk_master:
            self.error_update_callback("tk master not set for macro")
            return
        if not self.is_running:
            self.is_running = True
            self.status_update_callback("running")
            print("anti-afk macro started.")
            self.schedule_mouse_move()

    # stop macro ops
    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.after_id and self.tk_master:
                self.tk_master.after_cancel(self.after_id)
                self.after_id = None
            self.status_update_callback("idle")
            print("anti-afk macro stopped.")

    # sched mouse movement
    def schedule_mouse_move(self):
        if self.is_running and self.tk_master:
            self._move_mouse()
            self.after_id = self.tk_master.after(self.move_interval_ms, self.schedule_mouse_move)

    # perform mouse movement
    def _move_mouse(self):
        if not self.is_running:
            return

        try:
            roblox_windows = pygetwindow.getWindowsWithTitle('Roblox')
            if roblox_windows:
                roblox_window = roblox_windows[0]
                if roblox_window.isActive:
                    pydirectinput.moveRel(self.mouse_move_pixels, self.mouse_move_pixels, duration=0.025, relative=True)
                    current_time = time.strftime("%I:%M:%S %p")
                    self.status_update_callback(f"running (roblox active, last move: {current_time})")
                    print(f"mouse moved (roblox active) at {current_time}")
                else:
                    self.status_update_callback("running (roblox not active)")
                    print(f"roblox not active, skipped mouse move at {time.strftime('%I:%M:%S %p')}")
            else:
                self.status_update_callback("running (roblox not found)")
                print(f"roblox window not found, skipped mouse move at {time.strftime('%I:%M:%S %p')}")
        except Exception as e:
            print(f"err moving mouse: {e}")
            self.error_update_callback(f"err - {e}")
            self.stop() # stop macro on err