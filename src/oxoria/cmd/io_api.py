import os
import json
from pathlib import Path

from oxoria.ui.ui_var import UI_Var
from oxoria.global_var import GBVar

class IoAPI:
    def __init__(self):
        pass

    def save_oxoria_file(self, 
                         saving_path: str
                         ) -> None:
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
        with open(saving_path, "w", encoding="utf-8") as f:
            json.dump(save_dict, f, indent=2)

    def open_oxoria_file(self, 
                         opening_path: str | Path
                         ) -> dict | None:
        if not opening_path.isinstance(Path):
            opening_path = Path(opening_path)
        if not opening_path.exists():
            return None
        if opening_path.suffix != ".oxoria":
            return None
        try:
            with open(opening_path, "r", encoding="utf-8") as f:
                opening_file = json.load(f)
            return opening_file
        except:
            return None
        
    def open_resource_on_canvas(self,
                                img_path: str | Path
                                ) -> None:
        main_canvas = UI_Var.MAIN_CANVAS
        if main_canvas is None: 
            return
        main_canvas.handle_file_drop(path=str(img_path),
                                     event=None,
                                     open_from_ext=True)