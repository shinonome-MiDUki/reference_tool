from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from oxoria.ui.ui_var import UI_Var
from oxoria.global_var import GBVar
from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.cmd.app_api import AppAPI

class StdMenuCmd:
    def __init__(self):
        self.canvas_api = CanvasAPI()
        self.resource_api = ResourcesAPI()
        self.app_api = AppAPI()

    def save_as(self) -> None:
        main_window = UI_Var.MAIN_WINDOW
        if main_window is None:
            return
        saving_file, _ = QFileDialog.getSaveFileName(
            main_window,
            caption="Save file as ...",
            filter="Oxoria Canvas (*.oxoria)")
        if saving_file:
            saving_file = str(Path(saving_file).with_suffix(".oxoria"))
            self.canvas_api.save_oxoria_file(saving_path=saving_file)
            GBVar.OPENED_FILE = saving_file

    def save_file(self) -> None:
        opened_file = GBVar.OPENED_FILE
        if opened_file is None:
            self.save_as()
        else:
            self.canvas_api.save_oxoria_file(saving_path=opened_file)

    def open_resource(self) -> None:
        main_window = UI_Var.MAIN_WINDOW
        if main_window is None:
            return
        img_path, _ = QFileDialog.getOpenFileName(
            main_window,
            caption="Open file",
            filter="All files (*)")
        self.canvas_api.open_resource_on_canvas(img_path=img_path)

    def open_oxoria_file(self) -> None:
        main_window = UI_Var.MAIN_WINDOW
        if main_window is None:
            return
        oxoria_file_path, _ = QFileDialog.getOpenFileName(
            main_window,
            caption="Open file",
            filter="Oxoria Canvas (*.oxoria)")
        if oxoria_file_path is None:
            return
        self.canvas_api.open_oxoria_file(opening_path=oxoria_file_path)

    def new_canvas(self) -> None:
        self.save_file()
        self.canvas_api.clear_canvas()

    def export_canvas(self) -> None:
        main_window = UI_Var.MAIN_WINDOW
        if main_window is None:
            return
        archive_file_path, _ = QFileDialog.getSaveFileName(
            main_window,
            caption="Save canvas archive as ...",
            filter="Oxoria Canvas Archive (*.oxoarchive)")
        if archive_file_path:
            archive_file_path = Path(archive_file_path).with_suffix(".oxoarchive")
            self.canvas_api.wrap_canvas(archive_file_path)

    def new_window(self) -> None:
        self.app_api.open_new_window()

    def quit_app(self) -> None:
        self.save_file()
        self.app_api.quit_app()

    def force_quit_app(self) -> None:
        self.app_api.quit_app()
