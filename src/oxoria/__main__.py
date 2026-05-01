import sys
import psutil
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QPixmap
import setproctitle

from oxoria.ui.main_ui import MainWindow
from oxoria.ui.initial.initialise_ui import InitUI
from oxoria.cmd.search_api import SearchAPI
from oxoria.cmd.app_api import AppAPI
from oxoria.global_var import GBVar

def check_first_run() -> bool:
    settings = QSettings("App", "oxoria")
    print(settings.value("first_run", "true"))
    #settings.setValue("first_run", "true")
    if settings.value("first_run", "true") == "true":
        settings.setValue("first_run", "false")
        return True
    return False

def main():
    load_dotenv()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    splash_img_path = Path(__file__).resolve().parent / "_resources/assets/initial_image.jpg"
    splash = QSplashScreen(QPixmap(str(splash_img_path)))
    splash.show()
    splash.showMessage("Loading transformers", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
    
    search_api = SearchAPI()
    setproctitle.setproctitle("Oxoria 1.0")
    if check_first_run():
        win = InitUI()
    else:
        if QSettings("App", "oxoria").value("use_capture_monitor", "true") == "true":
            app_api = AppAPI()
            app_api.run_capture_monitor()
        win = MainWindow()
    win.show()
    GBVar.MAIN_APP = app  
    splash.finish(win)  
    sys.exit(app.exec())


if __name__ == "__main__":
    main()