from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QMovie
from PySide6.QtWidgets import QFrame


POLISH_ALPHABET_SPRITES = {
            "A": "Assets/Alfabet/A.png",
            "Ą": "Assets/Alfabet/A_.png",
            "B": "Assets/Alfabet/B.png",
            "C": "Assets/Alfabet/C.png",
            "Ć": "Assets/Alfabet/C_.png",
            "D": "Assets/Alfabet/D.png",
            "E": "Assets/Alfabet/E.png",
            "Ę": "Assets/Alfabet/E_.png",
            "F": "Assets/Alfabet/F.png",
            "G": "Assets/Alfabet/G.png",
            "H": "Assets/Alfabet/H.png",
            "I": "Assets/Alfabet/I.png",
            "J": "Assets/Alfabet/J.png",
            "K": "Assets/Alfabet/K.png",
            "L": "Assets/Alfabet/L.png",
            "Ł": "Assets/Alfabet/L_.png",
            "M": "Assets/Alfabet/M.png",
            "N": "Assets/Alfabet/N.png",
            "Ń": "Assets/Alfabet/N_.png",
            "O": "Assets/Alfabet/O.png",
            "Ó": "Assets/Alfabet/O_.png",
            "P": "Assets/Alfabet/P.png",
            "R": "Assets/Alfabet/R.png",
            "S": "Assets/Alfabet/S.png",
            "Ś": "Assets/Alfabet/S_.png",
            "T": "Assets/Alfabet/T.png",
            "U": "Assets/Alfabet/U.png",
            "W": "Assets/Alfabet/W.png",
            "Y": "Assets/Alfabet/Y.png",
            "Z": "Assets/Alfabet/Z.png",
            "Ź": "Assets/Alfabet/Z_.png",
            "Ż": "Assets/Alfabet/Z1_.png",
            "_": "Assets/Alfabet/podkreslenie.png"
        }

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

        # Preload all 7 stage pix maps into a list for fast rendering (stages 0 to 6)
        # Assumes files are named: Assets/stage_0.png, Assets/stage_1.png, etc.
        self.hangman_stages = []
        for i in range(1, 8):
            self.hangman_stages.append(QPixmap(f"Assets/Szubienica/Szubienica{i}.png"))

        self.current_word_display = ""

        alphabet_paths = {
            "A": "Assets/Alfabet/A.png", "Ą": "Assets/Alfabet/A_.png",
            "B": "Assets/Alfabet/B.png", "C": "Assets/Alfabet/C.png",
            "Ć": "Assets/Alfabet/C_.png", "D": "Assets/Alfabet/D.png",
            "E": "Assets/Alfabet/E.png", "Ę": "Assets/Alfabet/E_.png",
            "F": "Assets/Alfabet/F.png", "G": "Assets/Alfabet/G.png",
            "H": "Assets/Alfabet/H.png", "I": "Assets/Alfabet/I.png",
            "J": "Assets/Alfabet/J.png", "K": "Assets/Alfabet/K.png",
            "L": "Assets/Alfabet/L.png", "Ł": "Assets/Alfabet/L_.png",
            "M": "Assets/Alfabet/M.png", "N": "Assets/Alfabet/N.png",
            "Ń": "Assets/Alfabet/N_.png", "O": "Assets/Alfabet/O.png",
            "Ó": "Assets/Alfabet/O_.png", "P": "Assets/Alfabet/P.png",
            "R": "Assets/Alfabet/R.png", "S": "Assets/Alfabet/S.png",
            "Ś": "Assets/Alfabet/S_.png", "T": "Assets/Alfabet/T.png",
            "U": "Assets/Alfabet/U.png", "W": "Assets/Alfabet/W.png",
            "Y": "Assets/Alfabet/Y.png", "Z": "Assets/Alfabet/Z.png",
            "Ź": "Assets/Alfabet/Z_.png", "Ż": "Assets/Alfabet/Z1_.png",
            "_": "Assets/Alfabet/podkreslenie.png"
        }

        # Convert everything into pre-cached QPixmaps for smooth, hardware-backed rendering
        self.alphabet_sprites = {}
        for char, path in alphabet_paths.items():
            self.alphabet_sprites[char] = QPixmap(path)

    def change_image(self, new_image_path):
        self.base_pixmap = QPixmap(new_image_path)
        self.update()

    def unbuffered_update(self):
        """Slots the frame change signal directly into a widget repaint."""
        self.update()

    def set_error_count(self, errors):
        """Updates the error count from main.py and triggers a repaint."""
        # Clamp errors between 0 and 6 to prevent index crashes
        self.current_errors = max(0, min(errors, 6))
        self.update()

    def set_word_display(self, masked_word: str):
        """Receives the generated string from main.py and triggers a redraw."""
        self.current_word_display = masked_word
        self.update()

    def paintEvent(self, event):
        if self.base_pixmap.isNull():
            return

        painter = QPainter(self)

        # 1. Clear background with your theme color
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # 2. Draw the image to perfectly match the current widget dimensions
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
            dynamic_width = max(50, int(self.width() * 0.10))
            scaled_hangman = current_stage_pixmap.scaled(
                dynamic_width,
                dynamic_width,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x_pos_right = self.width() - scaled_hangman.width() - int(self.width() * 0.05)
            y_pos_top = int(self.height() * 0.11) - 2
            painter.drawPixmap(x_pos_right, y_pos_top, scaled_hangman)

        # --- DRAW PLAYER GIF ANIMATION (Bottom Left) ---
        current_frame_pixmap = self.sprite_movie.currentPixmap()
        if not current_frame_pixmap.isNull():
            dynamic_width = max(50, int(self.width() * 0.25))
            scaled_sprite = current_frame_pixmap.scaled(
                dynamic_width,
                dynamic_width,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            x_pos_left = self.width() - scaled_sprite.width()
            y_pos_bottom = self.height() - scaled_sprite.height()
            painter.drawPixmap(x_pos_left, y_pos_bottom, scaled_sprite)

        # --- MULTI-LINE WORD SPRITE RENDERING ---
        if self.current_word_display:
            # 1. Parse out the spacing tokens sent from main.py
            # generate_masked_word() gives us alternating formatting spaces: "M _ _  K O T "
            # True word breaks are marked by double spaces.
            raw_chars = list(self.current_word_display)
            words = []
            current_word_tokens = []

            i = 0
            while i < len(raw_chars):
                char = raw_chars[i]
                if char == " ":
                    if i + 1 < len(raw_chars) and raw_chars[i + 1] == " ":
                        if current_word_tokens:
                            words.append(current_word_tokens)
                            current_word_tokens = []
                        i += 2  # Skip formatting space
                        continue
                else:
                    current_word_tokens.append(char)
                i += 1
            if current_word_tokens:
                words.append(current_word_tokens)

            if words:
                # 2. Determine size parameters relative to screen layout width
                letter_size = max(16, int(self.width() * 0.04))
                standard_spacing = int(letter_size * 0.10)

                # Define row gaps (e.g., 30% of a letter size)
                row_gap = int(letter_size * 0.30)

                # 3. Calculate total vertical height taken up by all text rows combined
                total_lines = len(words)
                total_content_height = (total_lines * letter_size) + ((total_lines - 1) * row_gap)

                # Initial overall vertical alignment starting anchor
                base_start_y = (self.height() - total_content_height) // 2

                # 4. Draw each word on its own individual row line
                for row_idx, word_tokens in enumerate(words):
                    # Compute total horizontal width for *just* this individual row to center it
                    row_width = (len(word_tokens) * letter_size) + ((len(word_tokens) - 1) * standard_spacing)

                    start_x = (self.width() - row_width) // 2
                    current_y = base_start_y + (row_idx * (letter_size + row_gap))

                    for col_idx, char in enumerate(word_tokens):
                        sprite = self.alphabet_sprites.get(char)
                        if sprite and not sprite.isNull():
                            scaled_letter = sprite.scaled(
                                letter_size, letter_size,
                                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                            )
                            current_x = start_x + (col_idx * (letter_size + standard_spacing))
                            painter.drawPixmap(current_x, current_y, scaled_letter)

        painter.end()