import sys
import math
from pathlib import Path

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QDialog
)
from PySide6.QtCore import (
    Qt, QPoint, QLineF
)
from PySide6.QtGui import (
    QPainter, QColor, QBrush, QPixmap, QPen, QCursor
)

from oxoria.ui.canvas_area.graphics_item import ImageItem
from oxoria.cmd.resources_api import ResourcesAPI
from oxoria.cmd.canvas_api import CanvasAPI
from oxoria.cmd.std_menu_cmd import StdMenuCmd
from oxoria.ui.resources_lib.registering_dialog import RegisterResourcesDialog
from oxoria.ui.ui_var import UI_Var
from oxoria.global_var import GBVar

class MainCanvas(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)


        scene = QGraphicsScene(self)
        scene.setSceneRect(-UI_Var.CANVAS_RANGE, -UI_Var.CANVAS_RANGE, UI_Var.CANVAS_RANGE * 2, UI_Var.CANVAS_RANGE * 2)
        self.setScene(scene)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.setAcceptDrops(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        UI_Var.CANVAS_HEIGHT = self.size().height()
        self.centerOn(0, 0)
        self.scale(0.2, 0.2)  

        self.panning     = False
        self.pan_start   = QPoint()
        UI_Var.MAIN_CANVAS = self

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        transform = self.transform()
        scale = transform.m11()  
        
        base_step = 100
        
        if scale > 2.0:
            step = base_step / 2
        elif scale < 0.5:
            step = base_step * 2
        else:
            step = base_step

        left = rect.left()
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()

        start_x = math.floor(left / step) * step
        start_y = math.floor(top / step) * step

        thin_pen = QPen(QColor(60, 60, 60), 1.0 / scale)
        thick_pen = QPen(QColor(80, 80, 80), 1.5 / scale)

        x = start_x
        while x < right:
            painter.setPen(thick_pen if int(x) % int(step * 5) == 0 else thin_pen)
            painter.drawLine(QLineF(x, top, x, bottom))
            x += step

        y = start_y
        while y < bottom:
            painter.setPen(thick_pen if int(y) % int(step * 5) == 0 else thin_pen)
            painter.drawLine(QLineF(left, y, right, y))
            y += step

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning   = True
            self.pan_start = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.position().toPoint() - self.pan_start
            self.pan_start = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        if (event.mimeData().hasUrls() or 
            event.mimeData().hasFormat("application/oxoria_resources")):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if (event.mimeData().hasUrls() or 
            event.mimeData().hasFormat("application/oxoria_resources")):
            event.acceptProposedAction()

    def handle_file_drop(self, 
                         path: str, 
                         event = None,
                         open_from_ext: bool = False,
                         ) -> None:
        extension = Path(path).suffix.lstrip(".").lower()
        if extension == "oxoria":
            canvas_api = CanvasAPI()
            if GBVar.OPENED_FILE is not None:
                std_menu_cmd = StdMenuCmd()
                std_menu_cmd.new_canvas()
            canvas_api.open_oxoria_file(opening_path=path)
            return
        if extension not in ["bmp", "cur", "gif", "ico", "jfif", "jpeg",
                             "jpg", "pbm", "pgm", "png", "ppm", "svg", 
                             "svgz", "xbm", "xpm"]:
            return
        resources_api = ResourcesAPI()
        existance_status = resources_api.check_exists(img_hash=None,
                                                        img_path=path,
                                                        tolerance=0)
        img_hash = existance_status[0]
        if img_hash is None: 
            return
        if not existance_status[1]:
            img_hash = existance_status[0]
            resources_register_dialog = RegisterResourcesDialog()
            resources_register_dialog.draw_dialog(img_path=path, img_hash=img_hash)
            register_status = resources_register_dialog.exec()
            if register_status == QDialog.DialogCode.Rejected:
                return
        else:
            img_hash = existance_status[0]
            path = resources_api.pointer_to_path(img_hash)
        if event is None and not open_from_ext:
            return
        pm = QPixmap(path)
        if open_from_ext:
            cursor_glob_pos = QCursor.pos()
            scene_pos = self.mapToScene(self.mapFromGlobal(cursor_glob_pos))
        else:
            scene_pos = self.mapToScene(event.position().toPoint())
        if not pm.isNull():
            item = ImageItem(pm, scene_pos)
            item.original_path = path
            item.pointer = img_hash
            self.scene().addItem(item)

    def dropEvent(self, event):
        event_mime = event.mimeData()
        if event_mime.hasUrls():
            for url in event_mime.urls():
                img_path = url.toLocalFile()
                self.handle_file_drop(img_path, event)
        elif event_mime.hasFormat("application/oxoria_resources"):
            img_pointer_b = event_mime.data("application/oxoria_resources")
            img_pointer = str(img_pointer_b, encoding="utf-8")
            resources_api = ResourcesAPI()
            img_path = resources_api.pointer_to_path(img_pointer)
            self.handle_file_drop(img_path, event)
        event.acceptProposedAction()

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            factor = 1.0
            if event.key() == Qt.Key_Semicolon:
                factor = 1.10
            elif event.key() == Qt.Key_Colon:
                factor = 0.90
            self.scale(factor, factor)
            UI_Var.CANVAS_HEIGHT = self.size().height()
        else:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                for item in self.scene().selectedItems():
                    self.scene().removeItem(item)
            elif event.key() == Qt.Key_0 and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self.resetTransform()
                self.centerOn(0, 0)
            elif event.key() == Qt.Key_R:
                print("Group selected items - To be implemented")
                selected_items = self.scene().selectedItems()
                if selected_items:
                    img_path = selected_items[0].original_path
                    print(f"Attempting to register resource from path: {img_path}")
                    if img_path is not None:
                        self.handle_file_drop(path=img_path)
        super().keyPressEvent(event)