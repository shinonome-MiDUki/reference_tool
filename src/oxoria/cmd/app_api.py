import sys
import psutil
import subprocess
from pathlib import Path

from oxoria.global_var import GBVar

class AppAPI:
    def __init__(self):
        pass

    def run_capture_monitor(self) -> None:
        for proc in psutil.process_iter(["cmdline"]):
            cmdl = proc.info["cmdline"]
            if cmdl and cmdl[0] == "Oxoria Screen Capture Monitor":
                print("working")
                return None
        tasktray_script = Path(__file__).resolve().parents[1] / "ui/tasktray/tasktray_ui.py"
        subprocess.Popen([sys.executable, str(tasktray_script)], start_new_session=True)

    def open_new_window(self) -> None:
        app_root_dir = Path(__file__).resolve().parents[1]
        entry_script = app_root_dir / "__main__.py"
        if not entry_script.exists():
            print("Entry script not found")
            return  
        subprocess.Popen([sys.executable, str(entry_script)], start_new_session=True)

    def quit_app(self) -> None:
        main_app = GBVar.MAIN_APP
        if main_app is not None:
            main_app.quit()