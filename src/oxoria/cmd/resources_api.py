import json
import shutil
import os
import platform
from pathlib import Path

from PySide6.QtCore import QSettings

from oxoria.graphics.img.image_hash import ImageHashing
from oxoria.global_var import GBVar

class ResourcesAPI:
    def __init__(self, data_path: str | None = None):
        if platform.system() == "Darwin":
            os.environ["OMP_NUM_THREADS"] = "1"
        if data_path is not None:
            self.data_path = data_path
        else:
            self.data_path = str(GBVar.DATA_DIR)
        self.image_hash = ImageHashing(hash_mode="dhash", 
                                    hash_size=8, 
                                    hash_set_path=str(Path(self.data_path) / "img_process/image_hash_set.pkl"))
        
    def clone_resource_to_repo(self, 
                               original_path: str,
                               new_path: str,
                               ) -> None:
        if Path(new_path).exists():
            return
        shutil.copy2(original_path, new_path)

    def check_exists(self, 
                     img_hash: str | None, 
                     img_path: str | None,
                     tolerance: float = 0
                     ) -> tuple[str | None, bool | None]:
        if img_hash is None:
            if img_path is not None:
                img_hash = self.image_hash.generate_hash(image_path=img_path)
            else:
                return None, None
        hash_set = self.image_hash.get_hash_set()
        if tolerance == 0:
            return img_hash, self.image_hash.match_hash(my_hash=img_hash, 
                                        target_hash_set=hash_set)
        else:
            for target_hash in hash_set:
                if self.image_hash.compare_hash(my_hash=img_hash, 
                                          target_hash=target_hash, 
                                          tolerance=tolerance):
                    return img_hash, True
            return img_hash, False
        
    def get_resources_profile(self) -> dict:
        resources_profile_path = Path(self.data_path) / "resources_lib/resources_profile.json"
        if resources_profile_path.exists(): 
            with open(resources_profile_path, "r", encoding="utf-8") as f:
                current_profile = json.load(f)
            return current_profile
        else:
            return {}
        
    def make_resource_profile(self,
                              img_path: str,
                              name: str = None,
                              memo: str = None,
                              tags: list[str] = None,
                              make_clone_path: bool = True
                              ) -> dict:
        if tags is None:
            tags = []
        if make_clone_path:
            img_path = Path(self.data_path) / "resources_lib" / Path(img_path).name
        if name is None:
            name = Path(img_path).stem
        if memo is None:
            memo = ""
        profile = {
            "path": str(img_path),
            "name": name,
            "memo": memo,
            "tags": tags
        }
        return profile
        
    def write_resource_profile(self,
                             pointer: str,
                             profile: dict,
                             merge: bool = False
                             ) -> bool:
        if "path" not in profile:
            return False
        current_profile = self.get_resources_profile()
        resources_profile_path = Path(self.data_path) / "resources_lib/resources_profile.json"
        if merge and pointer in current_profile:
            existing_profile = current_profile[pointer]
            existing_profile.update(profile)
            profile = existing_profile
        current_profile[pointer] = profile
        with open(resources_profile_path, "w", encoding="utf-8") as f:
            json.dump(current_profile, f, ensure_ascii=False, indent=4)
        return True

    def import_resource(self, 
                        img_hash: str | None,
                        img_path: str | None,
                        profile: dict,
                        skip_existencce_check: bool = True,
                        tolerance: float = 0,
                        make_clone: bool = True
                        ) -> bool:
        if img_hash is None:
            if img_path is not None:
                img_hash = self.image_hash.generate_hash(image_path=img_path)
            else:
                return False
        do_proceed = True
        if not skip_existencce_check:
            do_proceed = not self.check_exists(img_hash=img_hash, 
                                               img_path=None, 
                                               tolerance=tolerance)[1]
        if not do_proceed: 
            return False
        hash_set = self.image_hash.get_hash_set()
        hash_set.add(img_hash)
        if not self.write_resource_profile(pointer=img_hash, 
                                    profile=profile):
            return False
        self.image_hash.write_hash(hash_value=img_hash,
                             hash_set=hash_set)
        if make_clone:
            self.clone_resource_to_repo(original_path=img_path,
                                       new_path=profile["path"])
        return True

    def pointer_to_path(self, 
                        pointer: str
                        ) -> str | None:
        pointer_set = self.image_hash.get_hash_set()
        if pointer not in pointer_set:
            return None
        current_profile = self.get_resources_profile()
        if pointer not in current_profile:
            return None
        return current_profile[pointer].get("path", None)

    def path_to_pointer(self, 
                         path: str
                         ) -> str | None:
        current_profile = self.get_resources_profile()
        for pointer, profile in current_profile.items():
            if profile.get("path", None) == path:
                return pointer
        return None

    def name_to_path(self, 
                    name: str
                    ) -> str | None:
        current_profile = self.get_resources_profile()
        for pointer, profile in current_profile.items():
            if profile.get("name", None) == name:
                return profile.get("path", None)
        return None

    def filter_pointer_with_tag(self, 
                        tag: str
                        ) -> list[str]:
        current_profile = self.get_resources_profile()
        result = []
        for pointer, profile in current_profile.items():
            if tag in profile.get("tags", []):
                result.append(pointer)
        return result

    def filter_pointer_with_category(self, 
                            category: str):
        current_profile = self.get_resources_profile()
        result = []
        for pointer, profile in current_profile.items():
            if profile.get("category", None) == category:
                result.append(pointer)
        return result

    def filter_pointer_with_memo(self, 
                         kw: str
                         ):
        pass

    def edit_memo(self, 
                  pointer: str, 
                  memo_text: str
                  ) -> None:
        self.write_resource_profile(pointer=pointer,
                                    profile={"memo": memo_text},
                                    merge=True)

    def edit_tags(self, 
                  pointer: str, 
                  tags: list[str], 
                  mode: str = "append"
                  ) -> None:
        current_profile = self.get_resources_profile()
        if pointer not in current_profile:
            return
        existing_tags = current_profile[pointer].get("tags", [])
        if mode == "append":
            new_tags = list(set(existing_tags + tags))
        elif mode == "remove":
            new_tags = [tag for tag in existing_tags if tag not in tags]
        else:
            return
        self.write_resource_profile(pointer=pointer,
                                    profile={"tags": new_tags},
                                    merge=True)

        