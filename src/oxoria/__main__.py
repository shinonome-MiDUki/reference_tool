import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

from oxoria.ui.main_ui import MainWindow
from oxoria.ui.initial.initialise_ui import InitUI
from oxoria.cmd.search_api import SearchAPI

def check_first_run():
    settings = QSettings("App", "oxoria")
    #settings.setValue("first_run", "true")
    if settings.value("first_run", "true") == "true":
        settings.setValue("first_run", "false")
        return True
    return False

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    search_api = SearchAPI() 

    win = InitUI() if check_first_run() else MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()