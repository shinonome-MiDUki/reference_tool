import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,QVBoxLayout, QHBoxLayout, QLineEdit, 
    QTreeWidget, QTreeWidgetItem,QLabel, QPushButton
)
from PySide6.QtGui import (
    QColor, QPixmap, QDrag
)
from PySide6.QtCore import (
    Qt, QMimeData, QSettings, Signal
)

from oxoria.ui.ui_var import UI_Var
from oxoria.cmd.search_api import SearchAPI

class ResourceIcon(QWidget):
    def __init__(self, 
                 pointer: str,
                 resource_name: str,
                 memo_text: str,
                 tags: list[str],
                 img_path: str, 
                 ) -> None:
        super().__init__()
        self.hlayout = QHBoxLayout(self)
        self.hlayout.setContentsMargins(4, 4, 4, 4)
        self.pointer = pointer
        self.resource_name = resource_name
        self.memo_text = memo_text
        self.tags = tags
        self.img_path = img_path
        self._set_icon()

    def _set_icon(self):
        self.thumbnail = QLabel()
        pixmap = QPixmap(self.img_path)
        self.thumbnail.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.thumbnail.setFixedSize(48, 48)
        self.hlayout.addWidget(self.thumbnail)

        text_layout = QVBoxLayout()
        self.title_label = QLabel(self.resource_name)
        self.title_label.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 12px;")
        self.title_label.setWordWrap(True)
        text_layout.addWidget(self.title_label)
        self.memo_label = QLabel(self.memo_text)
        self.memo_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        self.memo_label.setWordWrap(True)
        text_layout.addWidget(self.memo_label)
        tag_list = ", ".join([f"#{t}" for t in self.tags])
        self.tag_label = QLabel(tag_list)
        self.tag_label.setStyleSheet("color: #ffffff; font-size: 10px;")
        self.tag_label.setWordWrap(True)
        text_layout.addWidget(self.tag_label)
        self.hlayout.addLayout(text_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            drag_mime_data = QMimeData()
            drag_mime_data.setText(self.pointer)
            drag_mime_data.setData("application/oxoria_resources", self.pointer.encode("utf-8"))
            drag.setMimeData(drag_mime_data)
            drag.setPixmap(self.thumbnail.pixmap())
            drag.exec(Qt.CopyAction)

class SidePanel(QWidget):
    """
    上部：検索バー
    下部：ツリービュー（グループ + アイテム）
    幅は QSplitter によって制御される
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resources_index_path = Path(QSettings("App", "oxoria").value("central_repo_dir")) / "resources_lib/resources_profile.json"
        self.setMinimumWidth(UI_Var.SIDEBAR_MIN)
        self.setMaximumWidth(UI_Var.SIDEBAR_MAX)
        self._build_ui()
        self._apply_style()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── タイトルバー ──────────────────────
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(36)
        tb_layout = QHBoxLayout(title_bar)
        tb_layout.setContentsMargins(12, 0, 8, 0)

        title_label = QLabel("My Resources")
        title_label.setObjectName("titleLabel")

        icon_btn = QPushButton("···")
        icon_btn.setObjectName("iconBtn")
        icon_btn.setFixedSize(24, 24)
        icon_btn.setToolTip("More actions")

        tb_layout.addWidget(title_label)
        tb_layout.addStretch()
        tb_layout.addWidget(icon_btn)

        # ── 検索バー ──────────────────────────
        search_frame = QWidget()
        search_frame.setObjectName("searchFrame")
        sf_layout = QHBoxLayout(search_frame)
        sf_layout.setContentsMargins(8, 6, 8, 6)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search My Resources")
        self.search_box.setObjectName("searchBox")
        self.search_box.setClearButtonEnabled(True)
        self.search_box.editingFinished.connect(self._on_search_changed)

        sf_layout.addWidget(self.search_box)

        # ── フィルターボタン行 ─────────────────
        filter_frame = QWidget()
        filter_frame.setObjectName("filterFrame")
        ff_layout = QHBoxLayout(filter_frame)
        ff_layout.setContentsMargins(8, 0, 8, 4)
        ff_layout.setSpacing(4)

        for label in ("A", "B", "C"):
            btn = QPushButton(label)
            btn.setObjectName("filterBtn")
            btn.setCheckable(True)
            ff_layout.addWidget(btn)
        ff_layout.addStretch()

        # ── ツリービュー ──────────────────────
        self.tree = QTreeWidget()
        self.tree.setObjectName("SearchTree")
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setRootIsDecorated(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self._populate_tree()

        # ── 組み立て ──────────────────────────
        root_layout.addWidget(title_bar)
        root_layout.addWidget(search_frame)
        root_layout.addWidget(filter_frame)
        root_layout.addWidget(self.tree, stretch=1)

    def _populate_tree(self):
        with open(self.resources_index_path, "r") as f:
            resources_data = json.load(f)

        catagories = {}
        for pointer in resources_data:
            resource = resources_data[pointer]
            img_path = resource.get("path", "")
            name = resource.get("name", "Unnamed Resource")
            memo = resource.get("memo", "")
            tags = resource.get("tags", [])
            category = resource.get("category", "Uncategorized")
            if category not in catagories:
                tree_item = QTreeWidgetItem(self.tree)
                tree_item.setText(0, category)
                tree_item.setExpanded(True)
                font = tree_item.font(0)
                font.setBold(True)
                tree_item.setFont(0, font)
                tree_item.setForeground(0, QColor("#9D9D9D"))
                catagories[category] = tree_item
            if img_path == "" or not Path(img_path).exists():
                continue
            resource_icon = ResourceIcon(pointer=pointer,
                                resource_name=name, 
                                memo_text=memo, 
                                tags=tags, 
                                img_path=img_path)
            tree_item_to_append = catagories[category]
            child_item = QTreeWidgetItem(tree_item_to_append)
            self.tree.setItemWidget(child_item, 0, resource_icon)
            child_item.setSizeHint(0, resource_icon.sizeHint())

    def append_tree(self, 
                     pointer: str,
                     profile: dict
                     ) -> None:
        img_path = profile.get("path", "")
        name = profile.get("name", "Unnamed Resource")
        memo = profile.get("memo", "")
        tags = profile.get("tags", [])
        category = profile.get("category", "Uncategorized")
        for i in range(self.tree.topLevelItemCount()):
            catagory_item = self.tree.topLevelItem(i)
            if catagory_item.text(0) == category:
                tree_item_to_append = catagory_item
                break
        else:
            tree_item_to_append = QTreeWidgetItem(self.tree)
            tree_item_to_append.setText(0, category)
            tree_item_to_append.setExpanded(True)
            font = tree_item_to_append.font(0)
            font.setBold(True)
            tree_item_to_append.setFont(0, font)
            tree_item_to_append.setForeground(0, QColor("#9D9D9D"))
        if img_path == "" or not Path(img_path).exists():
            return
        resource_icon = ResourceIcon(pointer=pointer,
                            resource_name=name, 
                            memo_text=memo, 
                            tags=tags, 
                            img_path=img_path)
        child_item = QTreeWidgetItem(tree_item_to_append)
        self.tree.setItemWidget(child_item, 0, resource_icon)
        child_item.setSizeHint(0, resource_icon.sizeHint())

    def _filter_tree(self,
                     pointer_list: list[str] = None
                     ) -> None:
        if pointer_list is None:
            for i in range(self.tree.topLevelItemCount()):
                catagory_item = self.tree.topLevelItem(i)
                for j in range(catagory_item.childCount()):
                    child_item = catagory_item.child(j)
                    child_item.setHidden(False)
            return
        for i in range(self.tree.topLevelItemCount()):
            catagory_item = self.tree.topLevelItem(i)
            for j in range(catagory_item.childCount()):
                child_item = catagory_item.child(j)
                resource_icon = self.tree.itemWidget(child_item, 0)
                if resource_icon.pointer in pointer_list:
                    child_item.setHidden(False)
                else:
                    child_item.setHidden(True)

    def _search_item(self,
                     target_pointer: str
                     ) -> None:
        for i in range(self.tree.topLevelItemCount()):
            catagory_item = self.tree.topLevelItem(i)
            for j in range(catagory_item.childCount()):
                child_item = catagory_item.child(j)
                resource_icon = self.tree.itemWidget(child_item, 0)
                if resource_icon.pointer == target_pointer:
                    child_item.setHidden(False)
                else:
                    child_item.setHidden(True)

    def _on_search_changed(self):
        kw = self.search_box.text().strip()
        if kw == "":
            self._filter_tree()
            return
        search_api = SearchAPI()
        if kw.startswith("$"):
            kw = kw[1:]
            suitable_pointer_list = search_api.distance_search_kw(kw=self.search_box.text(),
                                                                return_num=1,
                                                                cutoff=0.5)
            if suitable_pointer_list and suitable_pointer_list[0] is not None:
                self._search_item(target_pointer=suitable_pointer_list[0])
            else:
                self._filter_tree()
        else:
            suitable_pointer_list = search_api.semantic_search_kw_to_pointer(kw=self.search_box.text(), 
                                                                                return_num=2)
            self._filter_tree(pointer_list=suitable_pointer_list)

    def _on_item_clicked(self, item, column):
        pass  

    def _apply_style(self):
        self.setStyleSheet("""
            SidePanel {
                background: #252526;
            }
            QWidget#titleBar {
                background: #252526;
                border-bottom: 1px solid #3C3C3C;
            }
            QLabel#titleLabel {
                color: #BBBBBB;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QPushButton#iconBtn {
                background: transparent;
                color: #BBBBBB;
                border: none;
                font-size: 16px;
                border-radius: 3px;
            }
            QPushButton#iconBtn:hover {
                background: #3A3A3A;
            }
            QWidget#searchFrame {
                background: #252526;
            }
            QLineEdit#searchBox {
                background: #3C3C3C;
                color: #D4D4D4;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
            }
            QLineEdit#searchBox:focus {
                border: 1px solid #007ACC;
            }
            QWidget#filterFrame {
                background: #252526;
            }
            QPushButton#filterBtn {
                background: #3C3C3C;
                color: #9D9D9D;
                border: none;
                border-radius: 3px;
                padding: 2px 8px;
                font-size: 11px;
            }
            QPushButton#filterBtn:hover {
                background: #4A4A4A;
                color: #D4D4D4;
            }
            QPushButton#filterBtn:checked {
                background: #007ACC;
                color: #FFFFFF;
            }
            QTreeWidget#SearchTree {
                color: #CCCCCC;
                border: none;
                font-size: 12px;
                outline: none;
            }
            QTreeWidget#SearchTree::item {
                padding: 3px 0;
            }
            QTreeWidget#SearchTree::item:hover {
                background: #2A2D2E;
            }
            QTreeWidget#SearchTree::item:selected {
                background: #094771;
            }
            QScrollBar:vertical {
                background: #252526;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #424242;
                border-radius: 4px;
            }
        """)