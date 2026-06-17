# -*- coding: utf-8 -*-
from typing import Optional, List, Dict, Set
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QPainter, QColor, QMovie, QPen, QPaintEvent
from PySide6.QtWidgets import QFrame, QWidget
from resolve_path import resolve_path


class ResponsiveBgFrame(QFrame):
    def __init__(self, image_path: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.base_pixmap: QPixmap = QPixmap(image_path)
        self.setAutoFillBackground(False)

        # --- Ustawienie animacji gracza ---
        self.sprite_movie: QMovie = QMovie(resolve_path("assets/animacja_gracza.gif"), parent=self)
        self.sprite_movie.frameChanged.connect(self.update)
        self.sprite_movie.start()

        # --- Ustawienie wisielca ---
        self.current_errors: int = 0

        self.hangman_stages: List[QPixmap] = []
        for i in range(1, 8):
            self.hangman_stages.append(QPixmap(resolve_path(f"assets/Szubienica/Szubienica{i}.png")))

        # --- Ustawienie słów ---
        self.current_word_display: Optional[str] = None
        self.pending_guess: Optional[str] = None
        self.guessed_letters_list: List[str] = []

        self.current_coins: int = 0
        self.coin_pixmap: QPixmap = QPixmap(resolve_path("assets/moneta.png"))

        # Ścieżki do liter z fontu
        alphabet_paths: Dict[str, str] = {
            "A": "assets/alfabet/A.png", "Ą": "assets/alfabet/A_.png",
            "B": "assets/alfabet/B.png", "C": "assets/alfabet/C.png",
            "Ć": "assets/alfabet/C_.png", "D": "assets/alfabet/D.png",
            "E": "assets/alfabet/E.png", "Ę": "assets/alfabet/E_.png",
            "F": "assets/alfabet/F.png", "G": "assets/alfabet/G.png",
            "H": "assets/alfabet/H.png", "I": "assets/alfabet/I.png",
            "J": "assets/alfabet/J.png", "K": "assets/alfabet/K.png",
            "L": "assets/alfabet/L.png", "Ł": "assets/alfabet/L_.png",
            "M": "assets/alfabet/M.png", "N": "assets/alfabet/N.png",
            "Ń": "assets/alfabet/N_.png", "O": "assets/alfabet/O.png",
            "Ó": "assets/alfabet/O_.png", "P": "assets/alfabet/P.png",
            "R": "assets/alfabet/R.png", "S": "assets/alfabet/S.png",
            "Ś": "assets/alfabet/S_.png", "T": "assets/alfabet/T.png",
            "U": "assets/alfabet/U.png", "W": "assets/alfabet/W.png",
            "Y": "assets/alfabet/Y.png", "Z": "assets/alfabet/Z.png",
            "Ź": "assets/alfabet/Z_.png", "Ż": "assets/alfabet/Z1_.png",
            "_": "assets/alfabet/podkreslenie.png"
        }

        # Wczytanie wszystkich assetów liter
        self.alphabet_sprites: Dict[str, QPixmap] = {}
        for char, path in alphabet_paths.items():
            self.alphabet_sprites[char] = QPixmap(resolve_path(path))

    def change_background_image(self, new_image_path: str) -> None:
        """ Aktualizacja grafiki tła """
        self.base_pixmap = QPixmap(new_image_path)
        self.update()

    def set_error_count(self, errors: int) -> None:
        """ Aktualizacji ilości błędów """
        # Clamp errors between 0 and 6 to prevent index crashes
        self.current_errors = max(0, min(errors, 6))
        self.update()

    def set_word_display(self, masked_word: str) -> None:
        """ Aktualizacja wyświetlanego słowa """
        self.current_word_display = masked_word
        self.update()

    def set_pending_guess(self, letter: Optional[str]) -> None:
        """ Aktualizacja oczekiwanego znaku """
        self.pending_guess = letter
        self.update()

    def set_guessed_letters(self, letters: Set[str]) -> None:
        """ Aktualizacja już sprawdzonych liter w postaci posortowanej listy """
        self.guessed_letters_list = sorted(list(letters))
        self.update()

    def set_coins(self, amount: int) -> None:
        """ Aktualizacja ilości monet"""
        self.current_coins = amount
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Główne zdarzenie rysowania widgetu."""
        if self.base_pixmap.isNull():
            return

        painter: QPainter = QPainter(self)

        self._draw_background(painter)
        self._draw_coins_hub(painter)
        self._draw_hangman(painter)
        self._draw_player_animation(painter)
        self._draw_word_display(painter)
        self._draw_pending_guess(painter)
        self._draw_guessed_letters(painter)

        painter.end()

    def _draw_background(self, painter: QPainter) -> None:
        """Rysuje tło dopasowane do wymiarów widgetu."""
        scaled_pixmap: QPixmap = self.base_pixmap.scaled(
            self.width(),
            self.height(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)

    def _draw_coins_hub(self, painter: QPainter) -> None:
        """Rysuje interfejs ilości monet w lewym górnym rogu."""
        if self.coin_pixmap.isNull():
            return

        painter.save()

        # Ustawienia retro czcionki
        font = painter.font()
        font.setFamily("Courier New")
        font.setPointSize(max(16, int(self.width() * 0.025)))
        font.setBold(True)
        painter.setFont(font)

        text: str = str(self.current_coins)
        fm = painter.fontMetrics()
        text_width: int = fm.horizontalAdvance(text)
        text_height: int = fm.height()

        # Obliczanie wymiarów ramki
        coin_size: int = max(24, int(self.width() * 0.04))
        padding: int = 10
        box_width: int = padding + coin_size + 10 + text_width + padding
        box_height: int = padding + max(coin_size, text_height) + padding

        # Rysowanie retro ramki pod monetą
        painter.setBrush(QColor(34, 34, 34, 240))
        painter.setPen(QPen(QColor(0, 0, 0), 3))
        painter.drawRect(15, 15, box_width, box_height)

        # Rysowanie monety
        scaled_coin: QPixmap = self.coin_pixmap.scaled(
            coin_size,
            coin_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        coin_y: int = 15 + (box_height - coin_size) // 2
        painter.drawPixmap(15 + padding, coin_y, scaled_coin)

        # Rysowanie złotego tekstu
        text_x: int = 15 + padding + coin_size + 10
        text_y: int = 15 + (box_height + fm.ascent() - fm.descent()) // 2
        painter.setPen(QColor("#f1c40f"))
        painter.drawText(text_x, text_y, text)

        painter.restore()

    def _draw_hangman(self, painter: QPainter) -> None:
        """Rysuje odpowiedni etap szubienicy w prawym górnym rogu."""
        current_stage_pixmap: QPixmap = self.hangman_stages[self.current_errors]
        if not current_stage_pixmap.isNull():
            dynamic_width: int = max(50, int(self.width() * 0.10))
            scaled_hangman: QPixmap = current_stage_pixmap.scaled(
                dynamic_width,
                dynamic_width,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
            x_pos_right: int = self.width() - scaled_hangman.width() - int(self.width() * 0.05) - 50
            y_pos_top: int = int(self.height() * 0.11) + 40
            painter.drawPixmap(x_pos_right, y_pos_top, scaled_hangman)

    def _draw_player_animation(self, painter: QPainter) -> None:
        """Rysuje animację gracza w prawym dolnym rogu."""
        current_frame_pixmap: QPixmap = self.sprite_movie.currentPixmap()
        if not current_frame_pixmap.isNull():
            dynamic_width: int = max(50, int(self.width() * 0.25))
            scaled_sprite_player: QPixmap = current_frame_pixmap.scaled(
                dynamic_width,
                dynamic_width,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
            x_pos_left: int = self.width() - scaled_sprite_player.width()
            y_pos_bottom: int = self.height() - scaled_sprite_player.height()
            painter.drawPixmap(x_pos_left, y_pos_bottom, scaled_sprite_player)

    def _draw_word_display(self, painter: QPainter) -> None:
        """Renderuje i układa odgadywane hasło (z obsługą zawijania słów)."""
        if not self.current_word_display:
            return

        raw_chars: List[str] = list(self.current_word_display)
        words: List[List[str]] = []
        current_word_tokens: List[str] = []

        i: int = 0
        while i < len(raw_chars):
            char: str = raw_chars[i]
            if char == " ":
                if i + 1 < len(raw_chars) and raw_chars[i + 1] == " ":
                    if current_word_tokens:
                        words.append(current_word_tokens)
                        current_word_tokens = []
                    i += 2  # Pominięcie spacji formatowania
                    continue
            else:
                current_word_tokens.append(char)
            i += 1

        if current_word_tokens:
            words.append(current_word_tokens)

        if words:
            letter_size: int = max(16, int(self.width() * 0.04))
            standard_spacing: int = int(letter_size * 0.10)
            row_gap: int = int(letter_size * 0.30)

            total_lines: int = len(words)
            total_content_height: int = (total_lines * letter_size) + ((total_lines - 1) * row_gap)
            base_start_y: int = (self.height() - total_content_height) // 2

            for row_idx, word_tokens in enumerate(words):
                row_width: int = (len(word_tokens) * letter_size) + ((len(word_tokens) - 1) * standard_spacing)
                start_x: int = (self.width() - row_width) // 2
                current_y: int = base_start_y + (row_idx * (letter_size + row_gap))

                for col_idx, char in enumerate(word_tokens):
                    sprite: Optional[QPixmap] = self.alphabet_sprites.get(char)
                    if sprite and not sprite.isNull():
                        scaled_letter: QPixmap = sprite.scaled(
                            letter_size,
                            letter_size,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.FastTransformation
                        )
                        current_x: int = start_x + (col_idx * (letter_size + standard_spacing))
                        painter.drawPixmap(current_x, current_y, scaled_letter)

    def _draw_pending_guess(self, painter: QPainter) -> None:
        """Rysuje wskaźnik literki oczekującej na zatwierdzenie (obok gracza)."""
        if not hasattr(self, 'pending_guess') or not self.pending_guess:
            return

        staged_sprite: Optional[QPixmap] = self.alphabet_sprites.get(self.pending_guess)

        if staged_sprite and not staged_sprite.isNull():
            indicator_size: int = max(24, int(self.width() * 0.04))

            scaled_indicator: QPixmap = staged_sprite.scaled(
                indicator_size,
                indicator_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )

            # Obliczenia bazujące na szerokości duszka gracza z _draw_player_animation
            player_width: int = max(50, int(self.width() * 0.25))
            x_pos: int = self.width() - player_width + int(self.width() * 0.06)
            y_pos: int = self.height() - player_width + int(self.height() * 0.055)

            painter.drawPixmap(x_pos, y_pos, scaled_indicator)

    def _draw_guessed_letters(self, painter: QPainter) -> None:
        """Rysuje zestawienie wcześniej zgadywanych liter (góra tablicy)."""
        if not hasattr(self, 'guessed_letters_list') or not self.guessed_letters_list:
            return

        used_letter_size: int = max(12, int(self.width() * 0.025))
        used_spacing: int = int(used_letter_size * 0.15)

        start_x_used: int = int(self.width() * 0.25)
        start_y_used: int = int(self.height() * 0.15)

        for i, letter in enumerate(self.guessed_letters_list):
            used_sprite: Optional[QPixmap] = self.alphabet_sprites.get(letter)

            if used_sprite and not used_sprite.isNull():
                scaled_used: QPixmap = used_sprite.scaled(
                    used_letter_size,
                    used_letter_size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation
                )

                current_x_used: int = start_x_used + (i * (used_letter_size + used_spacing))
                painter.drawPixmap(current_x_used, start_y_used, scaled_used)