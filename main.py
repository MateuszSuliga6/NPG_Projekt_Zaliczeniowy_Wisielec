import sys
import random 
from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon
from Responsive_Widget import ResponsiveBgFrame
from data_manager import DataManager
from stats_manager import StatsManager
from save_manager import SaveManager
import os
import ctypes

# --- NOWE: Importujemy nasz nowy lewy panel ---
from shop_panel import HudPanel

def resolve_path(relative_path: str) -> str:
    """
    Redirects relative paths to PyInstaller's temporary extraction
    directory if running as a compiled executable.
    """
    if hasattr(sys, '_MEIPASS'):
        # Running as a compiled .exe
        return os.path.join(sys._MEIPASS, relative_path)

    # Running normally as a Python script
    return os.path.join(os.path.abspath("."), relative_path)

class ShopDialog(QtWidgets.QDialog):
    def __init__(self, player_name: str, stats_manager: StatsManager, parent=None):
        super().__init__(parent)
        self.player_name = player_name
        self._stats_manager = stats_manager
        self.setWindowTitle(f"Sklep z mocami - {self.player_name}")
        self.resize(350, 250)

        layout = QtWidgets.QVBoxLayout(self)

        self.lbl_coins = QtWidgets.QLabel()
        self.lbl_coins.setStyleSheet("font-size: 16px; font-weight: bold; color: #f39c12;")
        self.lbl_coins.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_coins)

        # Przycisk: Podpowiedź
        self.btn_hint = QtWidgets.QPushButton("💡 Odkryj losową literę\n Cena: 30 monet")
        self.btn_hint.setMinimumHeight(60)
        self.btn_hint.clicked.connect(self.buy_hint)
        layout.addWidget(self.btn_hint)

        # Przycisk: Życie
        self.btn_life = QtWidgets.QPushButton("❤️ Dodatkowe życie (cofa błąd)\n Cena: 15 monet")
        self.btn_life.setMinimumHeight(60)
        self.btn_life.clicked.connect(self.buy_life)
        layout.addWidget(self.btn_life)

        btn_close = QtWidgets.QPushButton("Wróć do gry")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        self.update_ui()

    def update_ui(self):
        stats = self._stats_manager.get_player_stats(self.player_name)
        coins = stats.get("coins", 0)
        self.lbl_coins.setText(f"Twoje monety: {coins}")
        self.btn_hint.setEnabled(coins >= 30)
        self.btn_life.setEnabled(coins >= 15)

    def buy_hint(self):
        if self._stats_manager.purchase_item(self.player_name, "hints", 30):
            self.update_ui()
            if self.parent():
                self.parent().update_hud()

    def buy_life(self):
        if self._stats_manager.purchase_item(self.player_name, "extra_lives", 15):
            self.update_ui()
            if self.parent():
                self.parent().update_hud()


class StatsDialog(QtWidgets.QDialog):
    def __init__(self, player_name: str, parent=None): 
        super().__init__(parent)
        self.player_name = player_name
        self.setWindowTitle(f"Twoje Osiągnięcia i Historia - {self.player_name}")
        self.resize(450, 450)

        self._stats_manager = StatsManager()

        # Główny układ pionowy okna
        layout = QtWidgets.QVBoxLayout(self)

        # 1. SEKCJA: Tabela statystyk ogólnych
        layout.addWidget(QtWidgets.QLabel("<b>Ogólne statystyki:</b>"))
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Rozegrane gry", "Max Seria", "Skuteczność"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setFixedHeight(80)
        layout.addWidget(self.table)

        # Odstęp między sekcjami
        layout.addSpacing(15)

        # 2. SEKCJA: Lista wygranych haseł
        layout.addWidget(QtWidgets.QLabel("<b>Historia odgadniętych haseł:</b>"))
        self.words_list = QtWidgets.QListWidget()
        layout.addWidget(self.words_list)

        # 3. SEKCJA: Dolne przyciski akcji (układ poziomy)
        buttons_layout = QtWidgets.QHBoxLayout()

        # Przycisk resetowania
        self.btn_reset = QtWidgets.QPushButton("Resetuj statystyki")
        self.btn_reset.setStyleSheet("color: #c0392b; font-weight: bold;")  # Czerwony akcent ostrzegawczy
        self.btn_reset.clicked.connect(self.on_reset_clicked)
        buttons_layout.addWidget(self.btn_reset)

        # Przycisk zamknięcia
        btn_close = QtWidgets.QPushButton("Zamknij raport")
        btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_close)

        # Dodajemy układ przycisków do głównego layoutu okna
        layout.addLayout(buttons_layout)

        # Załadowanie kompletnych danych
        self.load_data()

    def load_data(self):
        p_stats = self._stats_manager.get_player_stats(self.player_name) 

        if p_stats:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QtWidgets.QTableWidgetItem(str(p_stats.get("games_played", 0))))
            self.table.setItem(0, 1, QtWidgets.QTableWidgetItem(str(p_stats.get("max_win_streak", 0))))
            self.table.setItem(0, 2, QtWidgets.QTableWidgetItem(f"{p_stats.get('accuracy_percentage', 0.0)}%"))

            history_words = p_stats.get("won_words_history", [])

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
        """Slot obsługujący bezpieczne czyszczenie statystyk z potwierdzeniem."""
        # Wyświetlamy okienko pytające z przyciskami Tak/Nie
        reply = QtWidgets.QMessageBox.question(
            self,
            "Potwierdzenie resetu",
            "Czy na pewno chcesz bezpowrotnie usunąć wszystkie statystyki i historię haseł?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No  # Domyślnie zaznaczony przycisk "Nie"
        )

        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # Czyszczenie pliku stats.json przez manager
            self._stats_manager.reset_all_stats()
            # Ponowne załadowanie widoku (pokaże zera i komunikat o braku gier)
            self.load_data()

            QtWidgets.QMessageBox.information(
                self, "Zresetowano", "Statystyki zostały pomyślnie wyczyszczone."
            )


class GameWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._data_manager = DataManager()
        self._stats_manager = StatsManager()
        self._save_manager = SaveManager()
        
        self.player_name = self.ask_for_player_name()
        self.setWindowTitle(f"Wisielec - Gra z interfejsem graficznym | Gracz: {self.player_name}")

        # Ustalenie layout głównego całego okna
        master_layout = QtWidgets.QVBoxLayout()
        master_layout.setContentsMargins(0, 0, 0, 0)
        self.setWindowIcon(QIcon(resolve_path("Assets/Logo.png")))
        master_layout.setSpacing(0)

        # Ustalenie istnienia paska dolnego i jego formatowania
        navigation_bar = QtWidgets.QFrame()
        navigation_bar.setObjectName("Navigation_bar")
        
        # --- ZMIANA: Retro styl CSS dla całego dolnego paska i jego elementów ---
        navigation_bar.setStyleSheet("""
            QFrame#Navigation_bar {
                background-color: #222222; 
                border-top: 4px solid #000000;
                min-width: 100px;
                max-height: 120px;
            }
            
            /* Globalny styl dla wszystkich przycisków i list */
            QPushButton, QComboBox {
                background-color: #5c5c5c;
                color: #ffffff;
                border-top: 3px solid #949494;
                border-left: 3px solid #949494;
                border-bottom: 3px solid #212121;
                border-right: 3px solid #212121;
                padding: 4px 10px; /* Dodany margines wewnętrzny */
                font-family: "Courier New", monospace;
                font-weight: 900;
                font-size: 14px; /* Zwiększona czcionka */
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
            
            /* -- NAPRAWA LISTY ROZWIJANEJ -- */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                background-color: #4f4f4f; /* Ciemniejsze tło dla sekcji strzałki */
                border-left: 2px solid #212121; /* Oddzielenie strzałki od tekstu */
            }
            
            /* Kanciasta, "pikselowa" strzałka */
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
                background-color: #ffffff; /* Biały kwadracik udający strzałkę */
            }
            
            /* Stylizacja okienka z listą elementów po kliknięciu */
            QComboBox QAbstractItemView {
                background-color: #222222;
                color: #ffffff;
                border: 2px solid #000000;
                selection-background-color: #5c5c5c;
                font-family: "Courier New", monospace;
            }
        """)

        # Ustalenie layout paska dolnego
        navigation_bar_layout = QtWidgets.QHBoxLayout(navigation_bar)
        navigation_bar_layout.setContentsMargins(10, 20, 10, 20)
        navigation_bar_layout.setSpacing(15)

        # Wybór poziomu (TERAZ JAKO POLE KLASY)
        self.combo_level = QtWidgets.QComboBox()
        self.combo_level.addItems(self._data_manager.get_available_levels())
        self._level = self.combo_level.currentText()
        self.combo_level.textActivated.connect(self.on_level_changed)

        # Wybór kategorii (TERAZ JAKO POLE KLASY)
        self.combo_category = QtWidgets.QComboBox()
        self.combo_category.addItems(self._data_manager.get_available_categories())
        self._category = self.combo_category.currentText()
        self.combo_category.setMaxVisibleItems(3)
        self.combo_category.textActivated.connect(self.on_category_changed)

        #  Układ siatki dla przycisków ---
        buttons_grid_widget = QtWidgets.QWidget()
        buttons_grid = QtWidgets.QGridLayout(buttons_grid_widget)
        buttons_grid.setContentsMargins(0, 0, 0, 0)
        buttons_grid.setSpacing(5)  # Odstępy między przyciskami

        # Tworzenie przycisków
        self.button_save_game = QtWidgets.QPushButton("Zapis stanu gry")
        self.button_load_game = QtWidgets.QPushButton("Odczyt stanu gry")
        self.button_rules = QtWidgets.QPushButton("Zasady gry")
        self.button_stats = QtWidgets.QPushButton("Statystyki")

        # Rozmieszczenie w siatce (wracamy do czystego 2x2, bez sklepu)
        buttons_grid.addWidget(self.button_save_game, 0, 0)
        buttons_grid.addWidget(self.button_load_game, 1, 0)
        buttons_grid.addWidget(self.button_rules, 0, 1)
        buttons_grid.addWidget(self.button_stats, 1, 1)

        # Podpięcie sygnałów pod metody
        self.button_save_game.clicked.connect(self.on_save_game_clicked)
        self.button_load_game.clicked.connect(self.on_load_game_clicked)
        self.button_rules.clicked.connect(self.on_rules_clicked)
        self.button_stats.clicked.connect(self.on_stats_clicked)

        self.button_next_word = QtWidgets.QPushButton("Losuj kolejne hasło")
        self.button_next_word.clicked.connect(self.button_next_word_click)

        # Zrownanie wysokosci
        self.combo_level.setMinimumHeight(60)
        self.combo_category.setMinimumHeight(60)
        self.button_next_word.setMinimumHeight(60)

        self.current_word = self.get_word()[0].upper()

        self.guessed_letters = set()
        self.wrong_guesses_counter = 0
        self.max_wrong_guesses = 6
        self.current_guess = None

        # Ustawienie głównego okna rozgrywki
        self.main_content = ResponsiveBgFrame(resolve_path("Assets/klasa_latwy.png"))
        
        # --- ZMIANA: Zmieniamy układ na HBox, żeby dodać panel po lewej ---
        main_layout = QtWidgets.QHBoxLayout(self.main_content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Inicjalizacja nowego, pływającego lewego panelu HUD
        self.hud_panel = HudPanel()
        self.hud_panel.setFixedWidth(130) # Ustala stałą szerokość lewego paska
        
        # Podpinamy sygnały z przycisków wewnątrz panelu
        self.hud_panel.btn_shop.clicked.connect(self.on_shop_clicked)
        self.hud_panel.btn_hint.clicked.connect(self.use_hint)
        self.hud_panel.btn_life.clicked.connect(self.use_life)

        # Dodajemy panel do głównego widoku dociskając go do lewej i do DOŁU
        main_layout.addWidget(
            self.hud_panel, 
            alignment=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignLeft
        )

        # --- FIX: Przekazanie pełnego stanu początkowego do rysowania przez QPainter ---
        self.main_content.set_word_display(self.generate_masked_word())
        self.main_content.set_error_count(self.wrong_guesses_counter)
        self.main_content.set_guessed_letters(self.guessed_letters)
        self.main_content.set_pending_guess(None)

        # Ustawienie elementów paska nawigacji (ZDECYDOWANIE MNIEJ ELEMENTÓW!)
        navigation_bar_layout.addWidget(self.button_next_word)
        navigation_bar_layout.addWidget(self.combo_level)
        navigation_bar_layout.addWidget(self.combo_category)
        navigation_bar_layout.addWidget(buttons_grid_widget)

        # Ustawianie ułożenia całego okna gry
        master_layout.addWidget(self.main_content)
        master_layout.addWidget(navigation_bar)
        master_layout.addStretch()

        container = QtWidgets.QWidget()
        container.setLayout(master_layout)
        self.setCentralWidget(container)
        
        self.update_hud()

    def ask_for_player_name(self) -> str:
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Witaj w grze!", "Podaj swój nick, aby śledzić statystyki i zbierać monety:",
            QtWidgets.QLineEdit.EchoMode.Normal, ""
        )
        if ok and text.strip():
            return text.strip()
        return "Gość"

    def update_hud(self):
        """Aktualizuje elementy lewego panelu na podstawie profilu gracza."""
        stats = self._stats_manager.get_player_stats(self.player_name)
        if stats:
            # Monety w rogu planszy (ResponsiveBgFrame)
            self.main_content.set_coins(stats.get("coins", 0))
            
            # Moce specjalne w lewym panelu HUD
            hints = stats.get('hints', 0)
            lives = stats.get('extra_lives', 0)
            self.hud_panel.update_inventory(hints, lives, self.wrong_guesses_counter)

    def use_hint(self):
        """Losuje nieodgadniętą literę i ją odkrywa, zużywając podpowiedź."""
        unrevealed = [char for char in self.current_word if char not in self.guessed_letters and char.isalpha()]
        if not unrevealed:
            return 
            
        if self._stats_manager.consume_item(self.player_name, "hints"):
            hint_letter = random.choice(list(set(unrevealed)))
            self.process_confirmed_guess(hint_letter)
            self.update_hud()

    def use_life(self):
        """Cofa licznik błędów o jeden, ratując przed powieszeniem."""
        if self.wrong_guesses_counter > 0:
            if self._stats_manager.consume_item(self.player_name, "extra_lives"):
                self.wrong_guesses_counter -= 1
                self.update_counter_display()
                self.update_hud()

    @QtCore.Slot()
    def on_shop_clicked(self) -> None:
        dialog = ShopDialog(self.player_name, self._stats_manager, self)
        dialog.exec()

    @QtCore.Slot()
    def on_save_game_clicked(self) -> None:
        state = {
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
        state = self._save_manager.load_state()

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
            self.main_content.change_image(resolve_path('Assets/klasa_latwy.png'))
        elif self._level == "Średni":
            self.main_content.change_image(resolve_path('Assets/klasa_sredni.png'))
        elif self._level == "Trudny":
            self.main_content.change_image(resolve_path('Assets/klasa_trudny.png'))

        self.combo_level.setCurrentText(self._level)
        self.combo_category.setCurrentText(self._category)
        
        self.update_hud()

        QtWidgets.QMessageBox.information(
            self, "Wczytano", "Gra została pomyślnie przywrócona!"
        )

    @QtCore.Slot()
    def on_rules_clicked(self) -> None:
        rules_text = (
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

        QtWidgets.QMessageBox.information(
            self,
            "Zasady gry",
            rules_text
        )

    @QtCore.Slot()
    def on_stats_clicked(self) -> None:
        dialog = StatsDialog(self.player_name, self) 
        dialog.exec()

    @QtCore.Slot()
    def on_level_changed(self, selected_text: str) -> None:
        self._level = selected_text
        self.current_guess = None
        self.main_content.set_pending_guess(None)

        if selected_text == "Łatwy" :
            self.main_content.change_image(resolve_path('Assets/klasa_latwy.png'))
        elif selected_text == "Średni":
            self.main_content.change_image(resolve_path('Assets/klasa_sredni.png'))
        elif selected_text == "Trudny" :
            self.main_content.change_image(resolve_path('Assets/klasa_trudny.png'))

        self.button_next_word_click()

    @QtCore.Slot()
    def on_category_changed(self, selected_text: str) -> None:
        self._category = selected_text
        self.current_guess = None
        self.main_content.set_pending_guess(None)
        self.button_next_word_click()

    @QtCore.Slot()
    def button_next_word_click(self) -> None:
        self.current_word = self.get_word()[0].upper()
        self.guessed_letters.clear()
        self.wrong_guesses_counter = 0

        self.main_content.set_guessed_letters(self.guessed_letters)
        self.update_word_display()
        self.update_counter_display()
        self.update_hud() 

    def update_word_display(self):
        self.main_content.set_word_display(self.generate_masked_word())

    def generate_masked_word(self) -> str:
        display_letters = []
        for letter in self.current_word:
            if letter in self.guessed_letters:
                display_letters.append(letter)
            elif letter.isspace() or letter in ["-", "'"]:
                display_letters.append(letter)
            else:
                display_letters.append("_")
        return " ".join(display_letters)

    def update_counter_display(self):
        self.main_content.set_error_count(self.wrong_guesses_counter)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            if self.current_guess is not None:
                guess = self.current_guess
                self.current_guess = None
                self.main_content.set_pending_guess(None)
                self.process_confirmed_guess(guess)
            return

        key_text = event.text()
        if not key_text or not key_text.isalpha():
            super().keyPressEvent(event)
            return

        potential_guess = key_text.upper()
        if potential_guess in self.guessed_letters:
            return

        self.current_guess = potential_guess
        self.main_content.set_pending_guess(self.current_guess)

    def process_confirmed_guess(self, guess: str):
        self.guessed_letters.add(guess)
        self.main_content.set_guessed_letters(self.guessed_letters)

        if guess in self.current_word:
            self.update_word_display()
            if "_" not in self.generate_masked_word():
                self.end_game(won=True)
        else:
            self.wrong_guesses_counter += 1
            self.update_counter_display()
            self.update_hud() 

            if self.wrong_guesses_counter >= self.max_wrong_guesses:
                self.end_game(won=False)

    def end_game(self, won: bool):
        self._save_manager.delete_save()

        total_letters = len(self.guessed_letters)
        correct_letters = total_letters - self.wrong_guesses_counter

        self._stats_manager.save_game_stats(
            level=self._level,
            category=self._category,
            result=won,
            total_letters_typed=total_letters,
            correct_letters_typed=correct_letters,
            word_text=self.current_word,
            player_name=self.player_name  
        )

        msg = QtWidgets.QMessageBox(self)
        if won:
            msg.setWindowTitle("Gratulacje!")
            msg.setText(f"Wygrałeś! Hasło to: {self.current_word}")
        else:
            msg.setWindowTitle("Koniec Gry")
            msg.setText(f"Przegrałeś. Prawidłowe hasło: {self.current_word}")
        msg.exec()

        self.button_next_word_click()
        self.update_hud() 

    def get_word(self) -> tuple[str,int]:
        result: tuple[list[str],int]|None = self._data_manager.get_final_word(self._level, self._category)

        if result is None:
            return f"[Brak haseł dla:\nPoziom: '{self._level}'\nKategoria: '{self._category}']", -1

        return "".join(result[0]), result[1]

    def resizeEvent(self, event):
        super().resizeEvent(event)
        current_width = self.centralWidget().width()
        target_game_height = int(current_width / 2)
        self.main_content.setFixedHeight(target_game_height)
        nav_height = self.findChild(QtWidgets.QFrame, "Navigation_bar").height()
        total_content_height = target_game_height + nav_height
        self.setFixedHeight(total_content_height)

if __name__ == "__main__":
    if os.name == 'nt': 
        myappid = 'mycompany.mygame.hangman.v1'  
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec())