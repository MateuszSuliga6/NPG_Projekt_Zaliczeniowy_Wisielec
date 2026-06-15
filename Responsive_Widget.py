from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QMovie
from PySide6.QtWidgets import QFrame


class ResponsiveBgFrame(QFrame):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.base_pixmap = QPixmap(image_path)
        self.setAutoFillBackground(False)


        # --- GIF MOVIE SETUP (Bottom Left) ---
        self.sprite_movie = QMovie("Assets/Gracz_Animacja/Animacja_Gracza_Gif.gif", parent=self)
        self.sprite_movie.frameChanged.connect(self.unbuffered_update)
        self.sprite_movie.start()

        # --- HANGMAN SETUP (Top Right) ---
        self.current_errors = 0

        # Pre-load all 7 stage pixmaps into a list for fast rendering (stages 0 to 6)
        # Assumes files are named: Assets/stage_0.png, Assets/stage_1.png, etc.
        self.hangman_stages = []
        self.hangman_stages.append(QPixmap(f"Assets/Szubienica/Szubienica1.png"))
        self.hangman_stages.append(QPixmap(f"Assets/Szubienica/Szubienica2.png"))
        self.hangman_stages.append(QPixmap(f"Assets/Szubienica/Szubienica3.png"))
        self.hangman_stages.append(QPixmap(f"Assets/Szubienica/Szubienica4.png"))
        self.hangman_stages.append(QPixmap(f"Assets/Szubienica/Szubienica5.png"))
        self.hangman_stages.append(QPixmap(f"Assets/Szubienica/Szubienica6.png"))
        self.hangman_stages.append(QPixmap(f"Assets/Szubienica/Szubienica7.png"))

    def change_image(self, new_image_path):
        self.base_pixmap = QPixmap(new_image_path)
        self.update()

    def unbuffered_update(self, frame_number):
        """Slots the frame change signal directly into a widget repaint."""
        self.update()

    def set_error_count(self, errors):
        """Updates the error count from main.py and triggers a repaint."""
        # Clamp errors between 0 and 6 to prevent index crashes
        self.current_errors = max(0, min(errors, 6))
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

        # --- DRAW HANGMAN STAGE (Top Right) ---
        current_stage_pixmap = self.hangman_stages[self.current_errors]

        if not current_stage_pixmap.isNull():
            # Define how large the hangman box should be (e.g., 150x150 pixels)
            hangman_size = 16

            scaled_hangman = current_stage_pixmap.scaled(
                hangman_size, hangman_size,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # Calculate coordinates for TOP-RIGHT corner
            # x = total width minus the width of the scaled hangman image minus padding
            # y = padding from the top edge
            x_pos_right = self.width() - scaled_hangman.width() - 15
            y_pos_top = 15

            painter.drawPixmap(x_pos_right, y_pos_top, scaled_hangman)

        current_frame_pixmap = self.sprite_movie.currentPixmap()

        if not current_frame_pixmap.isNull():
            # 1. Base the sprite's size dynamically on the frame width
            # (For example: Make the sprite's width exactly 10% of the game area width)
            dynamic_width = int(self.width() * 0.25)

            # 2. Enforce a minimum size so it doesn't turn into a tiny pixel on small screens
            if dynamic_width < 50:
                dynamic_width = 50

            # 3. Scale the current snapshot on the fly
            scaled_sprite = current_frame_pixmap.scaled(
                dynamic_width,
                dynamic_width,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            # 4. Anchor it to the bottom left corner using its new dynamic height
            x_pos = self.width() - scaled_sprite.width()
            y_pos = self.height() - scaled_sprite.height()

            # 5. Paint it
            painter.drawPixmap(x_pos, y_pos, scaled_sprite)