#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import ctypes
import random
from typing import Optional, Set

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon, QKeyEvent, QResizeEvent

# Autorsie moduły gry
from responsive_widget import ResponsiveBgFrame
from data_manager import DataManager
from stats_manager import StatsManager
from save_manager import SaveManager
from audio_manager import AudioManager
from shop_panel import HudPanel
from resolve_path import resolve_path

class ShopDialog(QtWidgets.QDialog):
    def __init__(self, player_name: str, stats_manager: StatsManager,
                 parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.player_name: str = player_name
        self._stats_manager: StatsManager = stats_manager
        self.setWindowTitle(f"Sklep z mocami - {self.player_name}")
        self.resize(350, 250)

        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)

        self.lbl_coins: QtWidgets.QLabel = QtWidgets.QLabel()
        self.lbl_coins.setStyleSheet("font-size: 16px; font-weight: bold; color: #f39c12;")
        self.lbl_coins.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_coins)

        self.btn_hint: QtWidgets.QPushButton = QtWidgets.QPushButton("💡 Odkryj losową literę\n Cena: 30 monet")
        self.btn_hint.setMinimumHeight(60)
        self.btn_hint.clicked.connect(self.buy_hint)
        layout.addWidget(self.btn_hint)

        self.btn_life: QtWidgets.QPushButton = QtWidgets.QPushButton("❤️ Dodatkowe życie (cofa błąd)\n Cena: 15 monet")
        self.btn_life.setMinimumHeight(60)
        self.btn_life.clicked.connect(self.buy_life)
        layout.addWidget(self.btn_life)

        btn_close: QtWidgets.QPushButton = QtWidgets.QPushButton("Wróć do gry")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.update_ui()

    def update_ui(self) -> None:
        """ Aktualizacja interfejsu sklepu na podstawie stanu konta gracza. """
        stats: dict = self._stats_manager.get_player_stats(self.player_name)
        coins: int = stats.get("coins", 0)
        self.lbl_coins.setText(f"Twoje monety: {coins}")
        self.btn_hint.setEnabled(coins >= 30)
        self.btn_life.setEnabled(coins >= 15)

    def buy_hint(self) -> None:
        """ Zakup podpowiedzi """
        if self._stats_manager.purchase_item(self.player_name, "hints", 30):
            self.update_ui()
            if self.parent():
                self.parent().update_hud()

    def buy_life(self) -> None:
        """ Zakup dodatkowego życia """
        if self._stats_manager.purchase_item(self.player_name, "extra_lives", 15):
            self.update_ui()
            if self.parent():
                self.parent().update_hud()

class StatsDialog(QtWidgets.QDialog):
    def __init__(self, player_name: str, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.player_name: str = player_name
        self.setWindowTitle(f"Twoje Osiągnięcia i Historia - {self.player_name}")
        self.resize(450, 450)

        self._stats_manager: StatsManager = StatsManager()

        layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(QtWidgets.QLabel("<b>Ogólne statystyki:</b>"))
        self.table: QtWidgets.QTableWidget = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Rozegrane gry", "Max Seria", "Skuteczność"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFixedHeight(80)
        layout.addWidget(self.table)

        layout.addSpacing(15)

        layout.addWidget(QtWidgets.QLabel("<b>Historia odgadniętych haseł:</b>"))
        self.words_list: QtWidgets.QListWidget = QtWidgets.QListWidget()
        layout.addWidget(self.words_list)

        buttons_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout()

        self.btn_reset: QtWidgets.QPushButton = QtWidgets.QPushButton("Resetuj statystyki")
        self.btn_reset.setStyleSheet("color: #c0392b; font-weight: bold;")
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        buttons_layout.addWidget(self.btn_reset)

        btn_close: QtWidgets.QPushButton = QtWidgets.QPushButton("Zamknij raport")
        btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_close)

        layout.addLayout(buttons_layout)

        self.load_data()

    def load_data(self) -> None:
        """ Pobranie i załadowanie statystyki oraz historii haseł do widżetów tabeli i listy. """
        p_stats: dict = self._stats_manager.get_player_stats(self.player_name)

        if p_stats:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QtWidgets.QTableWidgetItem(str(p_stats.get("games_played", 0))))
            self.table.setItem(0, 1, QtWidgets.QTableWidgetItem(str(p_stats.get("max_win_streak", 0))))
            self.table.setItem(0, 2, QtWidgets.QTableWidgetItem(f"{p_stats.get('accuracy_percentage', 0.0)}%"))

            history_words: list = p_stats.get("won_words_history", [])

            self.words_list.clear()
            if history_words:
                for word in history_words:
                    self.words_list.addItem(f"  {word}")
            else:
                self.words_list.addItem("Brak wygranych haseł na tym profilu. Czas coś wygrać!")
        else:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(0, 1, QtWidgets.QTableWidgetItem("0"))
            self.table.setItem(0, 2, QtWidgets.QTableWidgetItem("0.0%"))
            self.words_list.clear()
            self.words_list.addItem("Brak zapisanych gier. Rozegraj pierwszą partię!")

    @QtCore.Slot()
    def on_reset_clicked(self) -> None:
        """ Obsługa zdarzenie kliknięcia przycisku resetowania statystyk. """
        reply: QtWidgets.QMessageBox.StandardButton = QtWidgets.QMessageBox.question(
            self,
            "Potwierdzenie resetu",
            "Czy na pewno chcesz bezpowrotnie usunąć wszystkie statystyki i historię haseł?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self._stats_manager.reset_all_stats()
            self.load_data()
            QtWidgets.QMessageBox.information(
                self, "Zresetowano", "Statystyki zostały pomyślnie wyczyszczone."
            )

class GameWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._data_manager: DataManager = DataManager()
        self._stats_manager: StatsManager = StatsManager()
        self._save_manager: SaveManager = SaveManager()

        self._audio: AudioManager = AudioManager()
        self._audio.load_sound("correct", "correct.mp3")
        self._audio.load_sound("error", "error.mp3")
        self._audio.load_sound("win", "win.mp3")
        self._audio.load_sound("lose", "lose.mp3")

        self.player_name: str = self.ask_for_player_name()
        self.setWindowTitle(f"Wisielec - Gra z interfejsem graficznym | Gracz: {self.player_name}")

        master_layout: QtWidgets.QVBoxLayout = QtWidgets.QVBoxLayout()
        master_layout.setContentsMargins(0, 0, 0, 0)
        self.setWindowIcon(QIcon(resolve_path("assets/logo.png")))
        master_layout.setSpacing(0)

        navigation_bar: QtWidgets.QFrame = QtWidgets.QFrame()
        navigation_bar.setObjectName("Navigation_bar")

        navigation_bar.setStyleSheet("""
            QFrame#Navigation_bar {
                background-color: #222222; 
                border-top: 4px solid #000000;
                min-width: 100px;
                max-height: 120px;
            }

            QPushButton, QComboBox {
                background-color: #5c5c5c;
                color: #ffffff;
                border-top: 3px solid #949494;
                border-left: 3px solid #949494;
                border-bottom: 3px solid #212121;
                border-right: 3px solid #212121;
                padding: 4px 10px;
                font-family: "Courier New", monospace;
                font-weight: 900;
                font-size: 14px;
            }

            QPushButton:hover, QComboBox:hover {
                background-color: #6e6e6e;
            }

            QPushButton:pressed {
                border-top: 3px solid #212121;
                border-left: 3px solid #212121;
                border-bottom: 3px solid #949494;
                border-right: 3px solid #949494;
                padding-top: 6px; 
                padding-left: 12px;
            }

            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                background-color: #4f4f4f;
                border-left: 2px solid #212121;
            }

            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
                background-color: #ffffff;
            }

            QComboBox QAbstractItemView {
                background-color: #222222;
                color: #ffffff;
                border: 2px solid #000000;
                selection-background-color: #5c5c5c;
                font-family: "Courier New", monospace;
            }
        """)

        navigation_bar_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout(navigation_bar)
        navigation_bar_layout.setContentsMargins(10, 20, 10, 20)
        navigation_bar_layout.setSpacing(15)

        self.combo_level: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.combo_level.addItems(self._data_manager.get_available_levels())
        self._level: str = self.combo_level.currentText()
        self.combo_level.textActivated.connect(self.on_level_changed)

        self.combo_category: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.combo_category.addItems(self._data_manager.get_available_categories())
        self._category: str = self.combo_category.currentText()
        self.combo_category.setMaxVisibleItems(3)
        self.combo_category.textActivated.connect(self.on_category_changed)

        buttons_grid_widget: QtWidgets.QWidget = QtWidgets.QWidget()
        buttons_grid: QtWidgets.QGridLayout = QtWidgets.QGridLayout(buttons_grid_widget)
        buttons_grid.setContentsMargins(0, 0, 0, 0)
        buttons_grid.setSpacing(5)

        self.button_save_game: QtWidgets.QPushButton = QtWidgets.QPushButton("Zapis stanu gry")
        self.button_load_game: QtWidgets.QPushButton = QtWidgets.QPushButton("Odczyt stanu gry")
        self.button_rules: QtWidgets.QPushButton = QtWidgets.QPushButton("Zasady gry")
        self.button_stats: QtWidgets.QPushButton = QtWidgets.QPushButton("Statystyki")

        buttons_grid.addWidget(self.button_save_game, 0, 0)
        buttons_grid.addWidget(self.button_load_game, 1, 0)
        buttons_grid.addWidget(self.button_rules, 0, 1)
        buttons_grid.addWidget(self.button_stats, 1, 1)

        self.button_save_game.clicked.connect(self.on_save_game_clicked)
        self.button_load_game.clicked.connect(self.on_load_game_clicked)
        self.button_rules.clicked.connect(self.on_rules_clicked)
        self.button_stats.clicked.connect(self.on_stats_clicked)

        self.button_next_word: QtWidgets.QPushButton = QtWidgets.QPushButton("Losuj kolejne hasło")
        self.button_next_word.clicked.connect(self.button_next_word_click)

        self.combo_level.setMinimumHeight(60)
        self.combo_category.setMinimumHeight(60)
        self.button_next_word.setMinimumHeight(60)

        self.current_word: str = self.get_word()[0].upper()

        self.guessed_letters: Set[str] = set()
        self.wrong_guesses_counter: int = 0
        self.max_wrong_guesses: int = 6
        self.current_guess: Optional[str] = None

        self.main_content: ResponsiveBgFrame = ResponsiveBgFrame(resolve_path("assets/klasa_latwy.png"))

        main_layout: QtWidgets.QHBoxLayout = QtWidgets.QHBoxLayout(self.main_content)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.hud_panel: HudPanel = HudPanel()
        self.hud_panel.setFixedWidth(130)

        self.hud_panel.btn_shop.clicked.connect(self.on_shop_clicked)
        self.hud_panel.btn_hint.clicked.connect(self.use_hint)
        self.hud_panel.btn_life.clicked.connect(self.use_life)

        main_layout.addWidget(
            self.hud_panel,
            alignment=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self.main_content.set_word_display(self.generate_masked_word())
        self.main_content.set_error_count(self.wrong_guesses_counter)
        self.main_content.set_guessed_letters(self.guessed_letters)
        self.main_content.set_pending_guess(None)

        navigation_bar_layout.addWidget(self.button_next_word)
        navigation_bar_layout.addWidget(self.combo_level)
        navigation_bar_layout.addWidget(self.combo_category)
        navigation_bar_layout.addWidget(buttons_grid_widget)

        master_layout.addWidget(self.main_content)
        master_layout.addWidget(navigation_bar)
        master_layout.addStretch()

        container: QtWidgets.QWidget = QtWidgets.QWidget()
        container.setLayout(master_layout)
        self.setCentralWidget(container)

        self.update_hud()

    def ask_for_player_name(self) -> str:
        """ Wywołanie okna z pytaniem o nazwę gracza."""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Witaj w grze!", "Podaj swój nick, aby śledzić statystyki i zbierać monety:",
            QtWidgets.QLineEdit.EchoMode.Normal, ""
        )
        if ok and text.strip():
            return text.strip()
        return "Gość"

    def update_hud(self) -> None:
        """ Aktualizacja elementów lewego panelu (HUD) na podstawie profilu gracza."""
        stats: dict = self._stats_manager.get_player_stats(self.player_name)
        if stats:
            self.main_content.set_coins(stats.get("coins", 0))

            hints: int = stats.get("hints", 0)
            lives: int = stats.get("extra_lives", 0)
            self.hud_panel.update_inventory(hints, lives, self.wrong_guesses_counter)

    def use_hint(self) -> None:
        """ Losowanie nieodgadnięteje litery i ją odkrywa, zużywając podpowiedź z ekwipunku. """
        unrevealed: list[str] = [
            char for char in self.current_word
            if char not in self.guessed_letters and char.isalpha()
        ]
        if not unrevealed:
            return

        if self._stats_manager.consume_item(self.player_name, "hints"):
            hint_letter: str = random.choice(list(set(unrevealed)))
            self.process_confirmed_guess(hint_letter)
            self.update_hud()

    def use_life(self) -> None:
        """ Cofnięcie licznika błędów o jeden, zużywając dodatkowe życie ratujące przed powieszeniem. """
        if self.wrong_guesses_counter > 0:
            if self._stats_manager.consume_item(self.player_name, "extra_lives"):
                self.wrong_guesses_counter -= 1
                self.update_counter_display()
                self.update_hud()

    @QtCore.Slot()
    def on_shop_clicked(self) -> None:
        """ Otwarcie okna dialogowego sklepu z mocami specjalnymi. """
        dialog: ShopDialog = ShopDialog(self.player_name, self._stats_manager, self)
        dialog.exec()

    @QtCore.Slot()
    def on_save_game_clicked(self) -> None:
        """ Zapisanie bieżącego stanu rozgrywki do pliku i informacj użytkownika. """
        state: dict = {
            "level": self._level,
            "category": self._category,
            "current_word": self.current_word,
            "wrong_guesses_counter": self.wrong_guesses_counter,
            "guessed_letters": list(self.guessed_letters)
        }

        self._save_manager.save_state(state)

        QtWidgets.QMessageBox.information(
            self, "Zapisano", "Aktualny stan gry został pomyślnie zapisany!"
        )

    @QtCore.Slot()
    def on_load_game_clicked(self) -> None:
        """ Wczytanie zapisany stan gry, przywracając poziom, kategorię oraz postęp. """
        state: Optional[dict] = self._save_manager.load_state()

        if state is None:
            QtWidgets.QMessageBox.warning(
                self, "Błąd", "Nie znaleziono żadnego zapisanego stanu gry!"
            )
            return

        self._level = state["level"]
        self._category = state["category"]
        self.current_word = state["current_word"]
        self.wrong_guesses_counter = state["wrong_guesses_counter"]
        self.guessed_letters = set(state["guessed_letters"])

        self.update_word_display()
        self.update_counter_display()

        self.main_content.set_word_display(self.generate_masked_word())
        self.main_content.set_error_count(self.wrong_guesses_counter)
        self.main_content.set_guessed_letters(self.guessed_letters)
        self.main_content.set_pending_guess(None)

        if self._level == "Łatwy":
            self.main_content.change_background_image(resolve_path("assets/klasa_latwy.png"))
        elif self._level == "Średni":
            self.main_content.change_background_image(resolve_path("assets/klasa_sredni.png"))
        elif self._level == "Trudny":
            self.main_content.change_background_image(resolve_path("assets/klasa_trudny.png"))

        self.combo_level.setCurrentText(self._level)
        self.combo_category.setCurrentText(self._category)

        self.update_hud()

        QtWidgets.QMessageBox.information(
            self, "Wczytano", "Gra została pomyślnie przywrócona!"
        )

    @QtCore.Slot()
    def on_rules_clicked(self) -> None:
        """ Wyświetlanie okna dialogowego z zasadami i instrukcją obsługi gry. """
        rules_text: str = (
            "<h3><b>Zasady gry Wisielec</b></h3>"
            "<p>Twoim zadaniem jest odgadnięcie ukrytego hasła, zanim kat wykona wyrok!</p>"
            "<ul>"
            "<li><b>Wybór kategorii i poziomu:</b> Przed rozpoczęciem gry możesz wybrać poziom trudności oraz kategorię haseł za pomocą menu na dolnym pasku.</li>"
            "<li><b>Typowanie liter:</b> Naciśnij literę na klawiaturze. Wybrany znak pojawi się na ekranie jako podgląd.</li>"
            "<li><b>Zatwierdzanie ruchu:</b> Naciśnij klawisz <b>ENTER</b>, aby zatwierdzić literę i sprawdzić, czy znajduje się w haśle.</li>"
            "<li><b>Limit błędów:</b> Możesz pomylić się maksymalnie <b>6 razy</b>. Każda błędna litera dorysuje kolejny element szubienicy.</li>"
            "<li><b>Zapis i Odczyt stanu:</b> W każdej chwili możesz zapisać grę. Pamiętaj jednak, że system anty-cheat usunie Twój zapis w momencie wygranej lub przegranej!</li>"
            "</ul>"
            "<p><i>Powodzenia! Śledź swoje postępy i passę zwycięstw w zakładce 'Statystyki'.</i></p>"
        )

        QtWidgets.QMessageBox.information(self, "Zasady gry", rules_text)

    @QtCore.Slot()
    def on_stats_clicked(self) -> None:
        """ Otwiercie panelu ze statystykami powiązanymi z kontem gracza. """
        dialog: StatsDialog = StatsDialog(self.player_name, self)
        dialog.exec()

    @QtCore.Slot(str)
    def on_level_changed(self, selected_text: str) -> None:
        """ Zmiana tła rozgrywki w oparciu o nowo wybrany poziom trudności."""
        self._level = selected_text
        self.current_guess = None
        self.main_content.set_pending_guess(None)

        if selected_text == "Łatwy":
            self.main_content.change_background_image(resolve_path("assets/klasa_latwy.png"))
        elif selected_text == "Średni":
            self.main_content.change_background_image(resolve_path("assets/klasa_sredni.png"))
        elif selected_text == "Trudny":
            self.main_content.change_background_image(resolve_path("assets/klasa_trudny.png"))

        self.button_next_word_click()

    @QtCore.Slot(str)
    def on_category_changed(self, selected_text: str) -> None:
        """ Reakcja na zmianę kategorii z paska nawigacyjnego, resetując stan liter i losując hasło. """
        self._category = selected_text
        self.current_guess = None
        self.main_content.set_pending_guess(None)
        self.button_next_word_click()

    @QtCore.Slot()
    def button_next_word_click(self) -> None:
        """ Losowanie nowego słowa do odgadnięcia i reset licznika postępu. """
        self.current_word = self.get_word()[0].upper()
        self.guessed_letters.clear()
        self.wrong_guesses_counter = 0

        self.main_content.set_guessed_letters(self.guessed_letters)
        self.update_word_display()
        self.update_counter_display()
        self.update_hud()

    def update_word_display(self) -> None:
        """
        Aktualizuje główny widżet tak, aby poprawnie wyświetlał maskowane hasło.
        """
        self.main_content.set_word_display(self.generate_masked_word())

    def generate_masked_word(self) -> str:
        """
        Tworzy tekstową reprezentację zaszyfrowanego słowa.

        :return: Zamaskowane hasło ze spacjami pomiędzy literami i odsłoniętymi
                 znakami, które gracz już odgadł.
        """
        display_letters: list[str] = []
        for letter in self.current_word:
            if letter in self.guessed_letters:
                display_letters.append(letter)
            elif letter.isspace() or letter in ["-", "'"]:
                display_letters.append(letter)
            else:
                display_letters.append("_")
        return " ".join(display_letters)

    def update_counter_display(self) -> None:
        """ Wysłanie uaktualnionej liczby błędów do obiektu rysującego wisielca. """
        self.main_content.set_error_count(self.wrong_guesses_counter)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """ Event reagujący na  naciskane klawisze, rejestrując propozycje liter lub zatwierdzenia."""
        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            if self.current_guess is not None:
                guess: str = self.current_guess
                self.current_guess = None
                self.main_content.set_pending_guess(None)
                self.process_confirmed_guess(guess)
            return

        key_text: str = event.text()
        if not key_text or not key_text.isalpha():
            super().keyPressEvent(event)
            return

        potential_guess: str = key_text.upper()
        if potential_guess in self.guessed_letters:
            return

        self.current_guess = potential_guess
        self.main_content.set_pending_guess(self.current_guess)

    def process_confirmed_guess(self, guess: str) -> None:
        """ Przeważanie zaakceptowanej litery """
        self.guessed_letters.add(guess)
        self.main_content.set_guessed_letters(self.guessed_letters)

        if guess in self.current_word:
            self.update_word_display()
            self._audio.play("correct")

            if "_" not in self.generate_masked_word():
                self._audio.play("win")
                self.end_game(won=True)
        else:
            self.wrong_guesses_counter += 1
            self.update_counter_display()
            self.update_hud()
            self._audio.play("error")

            if self.wrong_guesses_counter >= self.max_wrong_guesses:
                self._audio.play("lose")
                self.end_game(won=False)

    def end_game(self, won: bool) -> None:
        """ Zakończenie rundy gry """
        self._save_manager.delete_save()

        total_letters: int = len(self.guessed_letters)
        correct_letters: int = total_letters - self.wrong_guesses_counter

        self._stats_manager.save_game_stats(
            level=self._level,
            result=won,
            total_letters_typed=total_letters,
            correct_letters_typed=correct_letters,
            word_text=self.current_word,
            player_name=self.player_name
        )

        msg: QtWidgets.QMessageBox = QtWidgets.QMessageBox(self)
        if won:
            msg.setWindowTitle("Gratulacje!")
            msg.setText(f"Wygrałeś! Hasło to: {self.current_word}")
        else:
            msg.setWindowTitle("Koniec Gry")
            msg.setText(f"Przegrałeś. Prawidłowe hasło: {self.current_word}")
        msg.exec()

        self.button_next_word_click()
        self.update_hud()

    def get_word(self) -> tuple[str, int]:
        """ Komunikacja się z DataManager, pobranie odpowiedniego hasło dla poziomu i kategorii. """
        result: Optional[tuple[list[str], int]] = self._data_manager.get_final_word(self._level, self._category)

        if result is None:
            return f"[Brak haseł dla:\nPoziom: '{self._level}'\nKategoria: '{self._category}']", -1

        return "".join(result[0]), result[1]

    def resizeEvent(self, event: QResizeEvent) -> None:
        """ Event aktualizacja wielkości okna, wymuszajacy poprawne proporcje """
        super().resizeEvent(event)
        current_width: int = self.centralWidget().width()
        target_game_height: int = int(current_width / 2)
        self.main_content.setFixedHeight(target_game_height)

        nav_height: int = self.findChild(QtWidgets.QFrame, "Navigation_bar").height()
        total_content_height: int = target_game_height + nav_height
        self.setFixedHeight(total_content_height)


if __name__ == "__main__":
    if os.name == "nt":
        myappid: str = "mycompany.mygame.hangman.v1"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
    window: GameWindow = GameWindow()
    window.show()
    sys.exit(app.exec())