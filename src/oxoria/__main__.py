import sys
import psutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings
import setproctitle

from oxoria.ui.main_ui import MainWindow
from oxoria.ui.initial.initialise_ui import InitUI
from oxoria.cmd.search_api import SearchAPI

def check_first_run() -> bool:
    settings = QSettings("App", "oxoria")
    #settings.setValue("first_run", "true")
    if settings.value("first_run", "true") == "true":
        settings.setValue("first_run", "false")
        return True
    return False

def check_keyboard_process() -> None:
    for proc in psutil.process_iter(["cmdline"]):
        cmdl = proc.info["cmdline"]
        if cmdl and cmdl[0] == "Oxoria Screen Capture Util":
            print("working")
            return None
    tasktray_script = Path(__file__).resolve().parent / "ui/tasktray/tasktray_ui.py"
    subprocess.Popen([sys.executable, str(tasktray_script)], start_new_session=True)

def main():
    load_dotenv()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    check_keyboard_process()
    search_api = SearchAPI() 

    setproctitle.setproctitle("Oxoria 1.0")
    win = InitUI() if check_first_run() else MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()