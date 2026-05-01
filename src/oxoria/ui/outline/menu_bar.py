import sys
import json
from pathlib import Path
from functools import partial

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QMenu, QToolBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from oxoria.global_var import GBVar
from oxoria.cmd.std_menu_cmd import StdMenuCmd
from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.cmd.search_api import SearchAPI
from oxoria.cmd.app_api import AppAPI

class MenuBar():
    def __init__(self, main_window: QMainWindow):
        self.main_window = main_window
        self.menu_bar = self.main_window.menuBar()
        with open(Path(GBVar.DATA_DIR) / "config/editor_config.json", "r", encoding="utf-8") as f:
            self.config = json.load(f)
        
    def build_menu(self):
        if "menu_bar" not in self.config:
            return
        std_menu_cmd = StdMenuCmd()
        canvas_api = CanvasAPI()
        resources_api = ResourcesAPI()
        search_api = SearchAPI()
        app_api = AppAPI()
        api_set = {
            "std": std_menu_cmd,
            "canvas": canvas_api,
            "resources": resources_api,
            "search": search_api,
            "app": app_api
        }
        for menu_item in self.config["menu_bar"]:
            menu_item_obj = self.menu_bar.addMenu(str(menu_item))
            if not isinstance(self.config["menu_bar"][menu_item], dict):
                continue
            for action_name, action_config in self.config["menu_bar"][menu_item].items():
                action = QAction(action_name, self.main_window)
                if action_config.get("shortcut", None) is not None:
                    action.setShortcut(action_config.get("shortcut"))
                if action_config.get("action", None) is not None:
                    cmd = str(action_config.get("action"))
                    action.triggered.connect(partial(exec, cmd, api_set))
                menu_item_obj.addAction(action)