from PySide6.QtWidgets import QFileDialog
from PySide6.QtGui import QCursor

from oxoria.ui.ui_var import UI_Var
from oxoria.global_var import GBVar
from oxoria.cmd.io_api import IoAPI

class StdMenuCmd:
    def __init__(self):
        self.io_api = IoAPI()

    def save_as(self) -> None:
        main_window = UI_Var.MAIN_WINDOW
        if main_window is None:
            return
        saving_file, _ = QFileDialog.getSaveFileName(main_window,
                                                     "Save file as ...",
                                                     "All files (*)")
        if saving_file:
            saving_file = f"{saving_file}.oxoria"
            self.io_api.save_oxoria_file(saving_path=saving_file)
            GBVar.OPENED_FILE = saving_file

    def save_file(self) -> None:
        opened_file = GBVar.OPENED_FILE
        if opened_file is None:
            self.save_as()
        else:
            self.io_api.save_oxoria_file(saving_path=opened_file)

    def open_resource(self) -> None:
        main_window = UI_Var.MAIN_WINDOW
        if main_window is None:
            return
        img_path, _ = QFileDialog.getOpenFileName(main_window,
                                               "Open file",
                                               "All file")
        self.io_api.open_resource_on_canvas(img_path=img_path)