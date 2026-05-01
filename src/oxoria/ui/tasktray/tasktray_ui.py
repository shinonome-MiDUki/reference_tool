import tkinter as tk
import subprocess
import os
import time
import json
import platform
import threading
import queue
from pathlib import Path

import setproctitle
from PIL import ImageGrab
from dotenv import load_dotenv
from pynput import keyboard

from oxoria.cmd.resources_api import ResourcesAPI

class TkinterWindow:
    def __init__(self,
                 master_tkroot: tk.Tk,
                 central_repo_dir: str,
                 saved_path: str):
        self.window = tk.Toplevel(master_tkroot)
        self.central_repo_dir = central_repo_dir
        self.saved_path = saved_path
        self.window.protocol("WM_DELETE_WINDOW", self._cancel_register)
        self.window.attributes("-topmost", True)
        self.tkinter_gui()

    def _register_to_json(self,
                          name_txt: tk.Entry,
                          memo_txt: tk.Entry
                          ) -> None:
        resource_name = name_txt.get().strip()
        resource_memo = memo_txt.get().strip()
        if self.central_repo_dir is None: 
            self.window.destroy()
            return
        resources_lib = Path(self.central_repo_dir) / "resources_lib"
        if not resources_lib.exists():
            resources_lib.mkdir(parents=True, exist_ok=True)
        temp_resources = resources_lib / "temp_resources.json"
        if temp_resources.exists():
            with open(temp_resources, "r", encoding="utf-8") as f:
                current_temp_resources = json.load(f)
        else:
            current_temp_resources = {}
        correct_file_path = resources_lib / f"{resource_name}.png"
        current_temp_resources[resource_name] = {
            "name" : resource_name,
            "memo" : resource_memo,
            "path" : str(correct_file_path),
            "tags" : ["a", "b", "c"]
        }
        if correct_file_path.exists():
            self.window.destroy()
            return
        os.rename(self.saved_path, str(correct_file_path))
        with open(temp_resources, "w", encoding="utf-8") as f:
            json.dump(current_temp_resources, f)
        self.window.quit()
        self.window.destroy()

    def _cancel_register(self):
        print("Cancel Register")
        if os.path.exists(self.saved_path):
            os.unlink(self.saved_path)
        self.window.quit()
        self.window.destroy()

    def tkinter_gui(self):
        self.window.geometry("650x300")
        self.window.title("OXORIA Screen Capture Registration")

        tk.Label(self.window,
                 text="resource name").place(x=30, y=30)
        name_txt = tk.Entry(self.window,
                            width=50)
        name_txt.place(x=130, y=30)

        tk.Label(self.window,
                 text="memo").place(x=30, y=65)
        memo_txt = tk.Entry(self.window,
                            width=50)
        memo_txt.place(x=130, y=65)

        tk.Button(self.window, 
                  text="Register", 
                  command=lambda: self._register_to_json(name_txt, memo_txt)).place(x=30, y=100)
        tk.Button(self.window, 
                  text="Cancel", 
                  command=lambda: self._cancel_register()).place(x=130, y=100)

        self.window.mainloop()

class CaptureImageTaskTray:
    def __init__(self):
        load_dotenv()
        self.central_repo_dir = os.environ.get("OXORIA_CENTRAL_REPO_DIR", None)
        self.msgq = queue.Queue()
        self.root = tk.Tk()
        self.root.withdraw()
        self.hotkey_map = {
            "<cmd>+<shift>+o" : self.capture_hotkey
        }

    def capture_hotkey(self):
        self.msgq.put("CAPTURE")

    def capture_to_oxoria(self):
        print("HelloWorld")
        resources_lib = Path(self.central_repo_dir) / "resources_lib"
        if not resources_lib.exists():
            resources_lib.mkdir(parents=True, exist_ok=True)
        temp_img_path = str(resources_lib / "temp_resource.png")
        if platform.system() == "Darwin":
            subprocess.run(["screencapture", "-i", temp_img_path])
        elif platform.system() == "Windows":
            subprocess.run(["snippingtool", "/clip", "/snip"])
            time.sleep(0.5)
            im = ImageGrab.grabclipboard()
            if not im:
                return
            im.save(temp_img_path)
        else:
            return
        if os.path.exists(temp_img_path):
            TkinterWindow(master_tkroot=self.root,
                        central_repo_dir=self.central_repo_dir,
                        saved_path=temp_img_path)

    def process_q(self):
        try:
            while True:
                message = self.msgq.get_nowait()
                if message == "CAPTURE":
                    self.capture_to_oxoria()
        except queue.Empty:
            pass
        self.root.after(100, self.process_q)

    def _hotkey_loop(self):
        with keyboard.GlobalHotKeys(self.hotkey_map) as h:
            h.join()

    def trigger(self):
        print("triggered")
        print(os.getpid())
        setproctitle.setproctitle("Oxoria Screen Capture Monitor")
        t = threading.Thread(target=self._hotkey_loop, 
                             daemon=True)
        t.start()
        self.process_q()
        self.root.mainloop()

if __name__ == "__main__":
    tray = CaptureImageTaskTray()
    tray.trigger()
