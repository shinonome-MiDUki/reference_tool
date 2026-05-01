import sys
import os
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QMenu, QToolBar
)
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QAction

from oxoria.ui.canvas_area.canvas import MainCanvas
from oxoria.ui.resources_lib.side_panel import SidePanel
from oxoria.ui.ux_widgets.splitter import Splitter
from oxoria.ui.ux_widgets.status_bar import HintBar
from oxoria.ui.outline.menu_bar import MenuBar
from oxoria.ui.ui_var import UI_Var
from oxoria.global_var import GBVar
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.cmd.search_api import SearchAPI

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        GBVar.DATA_DIR = str(QSettings("App", "oxoria").value("central_repo_dir"))
        self.check_temp_registered_resource()
        self.setWindowTitle("Oxoria 1.0")
        self.resize(1280, 800)
        self.setStyleSheet("background: #1E1E1E;")

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.menu_bar = MenuBar(self)
        self.menu_bar.build_menu()

        self.splitter = Splitter(Qt.Orientation.Horizontal)

        self.side_panel = SidePanel()
        self.canvas = MainCanvas()

        self.splitter.addWidget(self.side_panel)
        self.splitter.addWidget(self.canvas)

        self.splitter.setSizes([UI_Var.SIDEBAR_DEFAULT, 9999])
        self.splitter.setCollapsible(0, True)  
        self.splitter.setCollapsible(1, False) 

        main_layout.addWidget(self.splitter, stretch=1)
        main_layout.addWidget(HintBar())

    def check_temp_registered_resource(self):
        temp_resources_path = Path(QSettings("App", "oxoria").value("central_repo_dir")) / "resources_lib/temp_resources.json"
        if temp_resources_path.exists():
            resource_api = ResourcesAPI()
            with open(temp_resources_path, "r", encoding="utf-8") as f:
                temp_resources = json.load(f)
            for k, v in temp_resources.items():
                path = Path(v["path"])
                if not path.exists():
                    continue
                resource_profile = resource_api.make_resource_profile(img_path=str(path),
                                                                    name=v["name"],
                                                                    memo=v["memo"],
                                                                    tags=["a", "b", "c"])
                import_status = resource_api.import_resource(img_hash=None,
                                                             img_path=path,
                                                             profile=resource_profile,
                                                             skip_existencce_check=False,
                                                             make_clone=False)
                if not import_status:
                    continue
                search_api = SearchAPI()
                search_api.append_search_base(kw=v["memo"])
            temp_resources_path.unlink()
        else:
            return