import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout,
    QLabel, QFileDialog, QWidget, QLineEdit, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSettings

from oxoria.ui.resources_lib.side_panel import SidePanel
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.cmd.search_api import SearchAPI

class RegisterResourcesDialog(QDialog):
    def __init__(self):
        super().__init__()

    def draw_dialog(self, img_path: str, img_hash: str):
        self.setWindowTitle("Register Resources")
        self.setModal(True)
        self.img_path = img_path
        self.img_hash = img_hash
        layout = QVBoxLayout()
        self.image_preview_label = QLabel("Image Preview")
        self.image_preview_label.setAlignment(Qt.AlignCenter)
        self.image_preview_label.setStyleSheet("background-color: #ecf0f1; color: #2c3e50; font-size: 20px;")
        img = QPixmap(self.img_path)
        self.image_preview_label.setPixmap(img.scaled(600, 345, Qt.KeepAspectRatioByExpanding))
        self.image_preview_label.setFixedHeight(345)
        layout.addWidget(self.image_preview_label)
        
        input_fields_layout = QVBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Resource Name")
        input_fields_layout.addWidget(self.name_input)
        self.name_input.textEdited.connect(self.check_duplicate_name)
        self.name_check_label = QLabel()
        self.name_check_label.setText("Please input the image name")
        self.name_check_label.setStyleSheet("color: black;")
        input_fields_layout.addWidget(self.name_check_label)
        self.memo_input = QLineEdit()
        self.memo_input.setPlaceholderText("Memo")
        input_fields_layout.addWidget(self.memo_input)
        input_fields_layout.addStretch()
        layout.addLayout(input_fields_layout)

        button_layout = QHBoxLayout()
        self.register_button = QPushButton("Register resource")
        self.register_button.clicked.connect(self.register_and_open_resource)
        button_layout.addWidget(self.register_button)
        self.reg_without_open_button = QPushButton("Register without opening")
        self.reg_without_open_button.clicked.connect(self.register_without_open)
        button_layout.addWidget(self.reg_without_open_button)
        self.opt_out_register_button = QPushButton("Import without register")
        self.opt_out_register_button.clicked.connect(self.opt_out_register)
        button_layout.addWidget(self.opt_out_register_button)
        layout.addLayout(button_layout)
        layout.addLayout(input_fields_layout)

        self.setLayout(layout)

        resources_dir = Path(QSettings("App", "oxoria").value("central_repo_dir", "")) / "resources_lib"
        with open(resources_dir / "resources_profile.json", mode="r", encoding="utf-8") as f:
            resources_dict = json.load(f)
        self.resources_dict = resources_dict
        self.existing_path_set = set()
        self.existing_name_set = set()
        for k, v in self.resources_dict.items():
            if "path" in v:
                self.existing_path_set.add(v["path"])
            if "name" in v:
                self.existing_name_set.add(v["name"])
        
        self.resources_api = ResourcesAPI()

    def register_and_open_resource(self):
        self.register_resource()
        self.exec()

    def register_resource(self):
        input_name = str(self.name_input.text())
        if input_name in self.existing_name_set:
            return
        if str(self.name_input.text()).strip() == "":
            self.name_check_label.setText("Name cannot be empty")
            self.name_check_label.setStyleSheet("color: red;")
            return
        resource_profile = self.resources_api.make_resource_profile(img_path=str(self.img_path),
                                                                    name=str(self.name_input.text()),
                                                                    memo=str(self.memo_input.text()),
                                                                    tags=["a", "b", "c"])
        self.resources_api.import_resource(img_hash=self.img_hash,
                                           img_path=str(self.img_path), 
                                           profile=resource_profile)
        search_api = SearchAPI()
        search_api.append_search_base(kw=str(self.memo_input.text()))
        side_panel = SidePanel()
        side_panel.append_tree(pointer=self.img_hash,
                               profile=resource_profile)
        print("Resource registered:", resource_profile)
        self.accept()

    def opt_out_register(self):
        print("Resource import without register:", self.img_path)
        self.accept()

    def register_without_open(self):
        print("Resource registered without opening:", self.img_path)
        self.register_resource()
        self.reject()

    def check_duplicate_name(self):
        input_name = str(self.name_input.text())
        if input_name in self.existing_name_set:
            self.name_check_label.setText(f"{input_name} already exist")
            self.name_check_label.setStyleSheet("color: red;")
        else:
            self.name_check_label.setText("This name is available")
            self.name_check_label.setStyleSheet("color: black;")
