from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtWidgets import QFrame


class ResponsiveBgFrame(QFrame):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.base_pixmap = QPixmap(image_path)
        self.setAutoFillBackground(False)

    def change_image(self, new_image_path):
        self.base_pixmap = QPixmap(new_image_path)
        self.update()

    def paintEvent(self, event):
        if self.base_pixmap.isNull():
            return

        painter = QPainter(self)

        # Clear background with your theme color
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Draw the image to perfectly match the current widget dimensions
        scaled_pixmap = self.base_pixmap.scaled(
            self.width(),
            self.height(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()