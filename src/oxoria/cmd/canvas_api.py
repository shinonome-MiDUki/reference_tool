import os
import json
import shutil
from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QPointF

from oxoria.ui.ui_var import UI_Var
from oxoria.global_var import GBVar
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.ui.canvas_area.graphics_item import ImageItem

class CanvasAPI:
    def __init__(self):
        pass

    def make_oxoria_file(self) -> dict:
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        save_dict = {}
        scene = main_canvas.scene()
        item_list = scene.items()
        for graphics_item in item_list:
            pointer = graphics_item.pointer
            size_h = graphics_item.img_h
            size_w = graphics_item.img_w
            pos_x = graphics_item.pos().x()
            pos_y = graphics_item.pos().y()
            save_dict[pointer] = {
                "size_h" : size_h,
                "size_w" : size_w,
                "pos_x" : pos_x,
                "pos_y" : pos_y
            }
        return save_dict

    def save_oxoria_file(self, 
                         saving_path: str
                         ) -> None:
        save_dict = self.make_oxoria_file()
        with open(saving_path, "w", encoding="utf-8") as f:
            json.dump(save_dict, f, indent=2)

    def open_oxoria_file(self, 
                         opening_path: str | Path
                         ) -> None:
        if not opening_path.isinstance(Path):
            opening_path = Path(opening_path)
        if not opening_path.exists():
            return None
        if opening_path.suffix != ".oxoria":
            return None
        try:
            with open(opening_path, "r", encoding="utf-8") as f:
                oxoria_file_dict = json.load(f)
        except:
            return None
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        resource_api = ResourcesAPI()
        current_profile = resource_api.get_resources_profile()
        for pointer in oxoria_file_dict:
            if pointer not in current_profile:
                continue
            img_path = current_profile[pointer].get("path", None)
            img_trans = oxoria_file_dict[pointer]
            img_pm = QPixmap(img_path)
            img_item = ImageItem(img_pm, QPointF(img_trans["pos_x"], img_trans["pos_y"]))
            img_item.original_path = img_path
            img_item.pointer = pointer
            scaled_img = img_item.base_pixmap.scaled(
                int(img_trans["size_w"]), int(img_trans["size_h"]),
                aspectMode = Qt.KeepAspectRatio,
                mode = Qt.TransformationMode.SmoothTransformation
            )
            img_item.prepareGeometryChange()
            img_item.setPixmap(scaled_img)
            img_item.img_w = img_item.boundingRect().width()
            img_item.img_h = img_item.boundingRect().height()
            main_canvas.scene().addItem(img_item)
        
    def open_resource_on_canvas(self,
                                img_path: str | Path
                                ) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        main_canvas.handle_file_drop(path=str(img_path),
                                     event=None,
                                     open_from_ext=True)
        
    def clear_canvas(self) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        for graphics_item in main_canvas.scene().items():
            main_canvas.scene().removeItem(graphics_item)

    def wrap_canvas(self,
                    archive_path: str | Path
                    ) -> None:
        if not isinstance(archive_path, Path):
            archive_path = Path(archive_path)
        data_dir = Path(GBVar.DATA_DIR)
        temp_export_dir = data_dir / "temp_export"
        resources_dir = data_dir / "resources_lib"
        temp_export_dir.mkdir(parents=True, exist_ok=True)
        canvas_file_dict = self.make_oxoria_file()
        with open(temp_export_dir / "temp_canvas.oriana", "w", encoding="utf-8") as f:
            json.dump(canvas_file_dict, f)
        current_resources_profile_path = resources_dir / "resources_profile.json"
        if current_resources_profile_path.exists():
            with open(current_resources_profile_path, "r", encoding="utf-8") as f:
                current_resources_profile = json.load(f)
            temp_image_dir = temp_export_dir / "images"
            temp_export_dir.mkdir(parents=True, exist_ok=True)
            for pointer in current_resources_profile:
                if pointer not in canvas_file_dict:
                    del current_resources_profile[pointer]
                else:
                    img_path = current_resources_profile[pointer]["path"]
                    shutil.copy2(img_path, temp_image_dir)
        else:
            current_resources_profile = {}
        with open(temp_export_dir / "temp_resources_profile.json", "w", encoding="utf-8") as f:
            json.dump(current_resources_profile, f)
        shutil.make_archive(archive_path.with_suffix(""), format="zip", root_dir=temp_export_dir)
        os.rename(archive_path.with_suffix(".zip"), archive_path.with_suffix(".oxoarchive"))
        shutil.rmtree(temp_export_dir)