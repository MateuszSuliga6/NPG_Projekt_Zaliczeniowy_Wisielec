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

        self.current_word_display = None
        self.pending_guess = None
        self.guessed_letters_list = []

        # --- NOWE: HUD dla Monet ---
        self.current_coins = 0
        self.coin_pixmap = QPixmap("Assets/moneta.png")

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

    def set_pending_guess(self, letter: str or None):
        """Receives the staged letter waiting for Enter confirmation and redraws."""
        self.pending_guess = letter
        self.update()

    def set_guessed_letters(self, letters: set):
        """Receives the collection of already guessed letters and schedules a repaint."""
        # Convert to a sorted list so the assets don't bounce around randomly on screen
        self.guessed_letters_list = sorted(list(letters))
        self.update()
    
    def set_coins(self, amount: int):
        """Odbiera aktualny stan konta gracza z main.py i wymusza przerysowanie."""
        self.current_coins = amount
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
            Qt.TransformationMode.FastTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)

        # --- DRAW COIN HUD (Top Left) ---
        if not self.coin_pixmap.isNull():
            coin_size = max(24, int(self.width() * 0.04))
            scaled_coin = self.coin_pixmap.scaled(
                coin_size, coin_size,
                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation
            )
            # Rysowanie samej monety
            painter.drawPixmap(15, 15, scaled_coin)
            
            # Rysowanie tekstu ze stanem konta
            painter.save()
            font = painter.font()
            font.setFamily("Arial")
            font.setPointSize(max(14, int(self.width() * 0.025)))
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#f1c40f"))  # Złoty kolor (zółty)
            
            # Pozycjonowanie tekstu obok monety
            text_x = 15 + coin_size + 10
            text_y = 10 + (coin_size // 2) + (font.pointSize() // 2)
            painter.drawText(text_x, text_y, str(self.current_coins))
            painter.restore()

        # --- DRAW HANGMAN STAGE (Top Right) ---
        current_stage_pixmap = self.hangman_stages[self.current_errors]
        if not current_stage_pixmap.isNull():
            dynamic_width = max(50, int(self.width() * 0.10))
            scaled_hangman = current_stage_pixmap.scaled(
                dynamic_width,
                dynamic_width,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
            x_pos_right = self.width() - scaled_hangman.width() - int(self.width() * 0.05)
            y_pos_top = int(self.height() * 0.11) - 2
            painter.drawPixmap(x_pos_right, y_pos_top, scaled_hangman)

        # --- DRAW PLAYER GIF ANIMATION (Bottom Left) ---
        current_frame_pixmap = self.sprite_movie.currentPixmap()
        if not current_frame_pixmap.isNull():
            dynamic_width = max(50, int(self.width() * 0.25))
            scaled_sprite_player = current_frame_pixmap.scaled(
                dynamic_width,
                dynamic_width,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
            x_pos_left = self.width() - scaled_sprite_player.width()
            y_pos_bottom = self.height() - scaled_sprite_player.height()
            painter.drawPixmap(x_pos_left, y_pos_bottom, scaled_sprite_player)

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
                                Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation
                            )
                            current_x = start_x + (col_idx * (letter_size + standard_spacing))
                            painter.drawPixmap(current_x, current_y, scaled_letter)

        # --- DRAW PENDING GUESS IMAGE VERIFICATION ---
        # Checks if there is currently a letter staged waiting for confirmation
        if hasattr(self, 'pending_guess') and self.pending_guess:
            # Look up the custom PNG asset matching the staged letter character
            staged_sprite = self.alphabet_sprites.get(self.pending_guess)

            if staged_sprite and not staged_sprite.isNull():
                # 1. Size the validation asset dynamically (e.g., 6% of your active layout width)
                indicator_size = max(24, int(self.width() * 0.04))

                # 2. Rescale the letter asset smoothly
                scaled_indicator = staged_sprite.scaled(
                    indicator_size,
                    indicator_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation
                )

                # 3. COORDINATE LAYOUT RULES (Position it manually here)
                # Left placement padding offset
                x_pos = self.width() - scaled_sprite_player.width() + int(self.width() * 0.06)
                y_pos = self.height() - scaled_sprite_player.height() + int(self.height() * 0.055)

                # 4. Paint the custom graphics frame
                painter.drawPixmap(x_pos, y_pos, scaled_indicator)

                # Optional: If you want a decorative border or small textual prompt next to it,
                # you can overlay painter details here using standard configuration settings.
        # --- DRAW ALREADY USED LETTERS ASSETS (Top-Left Alignment) ---
        if hasattr(self, 'guessed_letters_list') and self.guessed_letters_list:
            # 1. Size the used letter icons dynamically (e.g., 2.5% of your active layout width)
            used_letter_size = max(12, int(self.width() * 0.025))
            used_spacing = int(used_letter_size * 0.15)

            # Starting coordinates for our "Used Letters" deck row
            start_x_used = int(self.width() * 0.25)
            start_y_used = int(self.height() * 0.15)

            # Optional: Draw a small text title above the used letter row
            painter.save()
            font = painter.font()
            font.setFamily("Arial")
            font.setPointSize(max(10, int(self.width() * 0.015)))
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#7f8c8d"))  # Muted grey slate color
            painter.restore()

            # 2. Iterate and paint each unique used asset emblem side-by-side
            for i, letter in enumerate(self.guessed_letters_list):
                used_sprite = self.alphabet_sprites.get(letter)

                if used_sprite and not used_sprite.isNull():
                    scaled_used = used_sprite.scaled(
                        used_letter_size,
                        used_letter_size,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.FastTransformation
                    )

                    # Calculate horizontal shifting per letter item
                    current_x_used = start_x_used + (i * (used_letter_size + used_spacing))

                    # Optional wrap checking: If your row goes too far right,
                    # you can add basic line wrapping logic here using floor division.

                    painter.drawPixmap(current_x_used, start_y_used, scaled_used)
        painter.end()