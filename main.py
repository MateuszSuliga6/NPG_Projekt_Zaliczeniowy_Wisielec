import sys
from PySide6 import QtCore, QtWidgets

from data_manager import DataManager
from stats_manager import StatsManager
from save_manager import SaveManager


class StatsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Statystyki Graczy")
        self.resize(500, 300)

        # Inicjalizacja managera, żeby pobrać świeże dane
        self._stats_manager = StatsManager()

        # Główny układ okna dialogowego
        layout = QtWidgets.QVBoxLayout(self)

        # Tworzenie tabeli
        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Gracz", "Rozegrane gry", "Max Seria", "Skuteczność"])

        # Ładne rozciąganie kolumn, żeby wypełniły okno
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # Blokada edycji

        layout.addWidget(self.table)

        # Przycisk zamknięcia
        btn_close = QtWidgets.QPushButton("Zamknij")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

        # Załadowanie danych do tabeli
        self.load_data()

    def load_data(self):
        # Pobieramy pełną strukturę z pliku JSON
        stats = self._stats_manager._read_json()
        players = stats.get("players", {})

        self.table.setRowCount(len(players))

        # Wypełnianie tabeli wiersz po wierszu
        for row, player_name in enumerate(players.keys()):
            # Korzystamy z get_player_stats, bo ona automatycznie liczy % skuteczności
            p_stats = self._stats_manager.get_player_stats(player_name)

            if p_stats:
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(player_name))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(p_stats["games_played"])))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(p_stats["max_win_streak"])))
                self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{p_stats['accuracy_percentage']}%"))



class GameWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.resize(800, 600)
        self.setWindowTitle(f"Wisielec - Gra z interfejsem graficznym")
        self._data_manager = DataManager()
        self._save_manager = SaveManager()

        # Ustalenie layout głównego całego okna
        master_layout = QtWidgets.QVBoxLayout()
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)

        # Ustalenie istnienia paska dolnego i jego formatowania
        navigation_bar = QtWidgets.QFrame()
        navigation_bar.setObjectName("Navigation_bar")
        # Color added for debug, change later
        navigation_bar.setStyleSheet(" background-color: #2c3e50; min-width: 100px; max-height: 100px")

        # Ustalenie layout paska dolnego
        navigation_bar_layout = QtWidgets.QHBoxLayout(navigation_bar)
        navigation_bar_layout.setContentsMargins(10, 20, 10, 20)
        navigation_bar_layout.setSpacing(15)

        # Wybór poziomu
        combo_level = QtWidgets.QComboBox()
        combo_level.addItems(self._data_manager.get_available_levels())
        self._level = combo_level.currentText()
        combo_level.textActivated.connect(self.on_level_changed)

        # Wybór kategorii
        combo_category = QtWidgets.QComboBox()
        combo_category.addItems(self._data_manager.get_available_categories())
        self._category = combo_category.currentText()
        combo_category.setMaxVisibleItems(3)
        combo_category.textActivated.connect(self.on_category_changed)



        #  Układ siatki dla 4 przycisków ---
        buttons_grid_widget = QtWidgets.QWidget()
        buttons_grid = QtWidgets.QGridLayout(buttons_grid_widget)
        buttons_grid.setContentsMargins(0, 0, 0, 0)
        buttons_grid.setSpacing(5)  # Odstępy między przyciskami

        # Tworzenie przycisków
        self.button_save_game = QtWidgets.QPushButton("Zapis stanu gry")
        self.button_load_game = QtWidgets.QPushButton("Odczyt stanu gry")
        self.button_rules = QtWidgets.QPushButton("Zasady gry")
        self.button_stats = QtWidgets.QPushButton("Statystyki")

        # Rozmieszczenie w siatce: addWidget(widget, wiersz, kolumna)
        # Kolumna 1
        buttons_grid.addWidget(self.button_save_game, 0, 0)
        buttons_grid.addWidget(self.button_load_game, 1, 0)
        # Kolumna 2
        buttons_grid.addWidget(self.button_rules, 0, 1)
        buttons_grid.addWidget(self.button_stats, 1, 1)

        # Podpięcie sygnałów pod przyszłe metody (sloty)
        self.button_save_game.clicked.connect(self.on_save_game_clicked)
        self.button_load_game.clicked.connect(self.on_load_game_clicked)
        self.button_rules.clicked.connect(self.on_rules_clicked)
        self.button_stats.clicked.connect(self.on_stats_clicked)

        self.button_next_word = QtWidgets.QPushButton("Losuj kolejne hasło")

        self.current_word = self.get_word()[0].upper()

        self.guessed_letters = set()
        self.wrong_guesses_counter = 0
        self.max_wrong_guesses = 6

        # Display the initial masked word
        self.update_counter_display()
        self.text = QtWidgets.QLabel(self.generate_masked_word(), alignment = QtCore.Qt.AlignmentFlag.AlignCenter)

        _font = self.text.font()
        _font.setPointSize(24)
        _font.setBold(True)
        self.text.setFont(_font)

        # Ustawienie elementów paska bocznego
        navigation_bar_layout.addWidget(self.button_next_word)
        navigation_bar_layout.addWidget(combo_level)
        navigation_bar_layout.addWidget(combo_category)
        # Ustawienie elementów paska nawigacji
        navigation_bar_layout.addWidget(self.button_next_word)
        navigation_bar_layout.addWidget(combo_level)
        navigation_bar_layout.addWidget(combo_category)

        # Wrzucamy siatkę z 4 przyciskami zamiast starego labela
        navigation_bar_layout.addWidget(buttons_grid_widget)
        self.button_next_word.clicked.connect(self.button_next_word_click)

        # Ustawienie głównego okna rozgrywki
        main_content = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(main_content)
        main_layout.addWidget(self.text)

        # Ustawianie ułożenia całego okna gry
        master_layout.addWidget(main_content)
        master_layout.addWidget(navigation_bar)
        container = QtWidgets.QWidget()
        container.setLayout(master_layout)
        self.setCentralWidget(container)

    @QtCore.Slot()
    def on_save_game_clicked(self) -> None:
        #Slot obsługujący zapis aktualnego stanu rozgrywki.
        # Ponieważ guessed_letters to Pythonowy `set` (zbiór), musimy go
        # zmienić na listę, bo JSON nie potrafi zapisać zbiorów bezpośrednio.
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
        #Slot obsługujący wczytanie zapisanego stanu rozgrywki.
        state = self._save_manager.load_state()

        if state is None:
            QtWidgets.QMessageBox.warning(
                self, "Błąd", "Nie znaleziono żadnego zapisanego stanu gry!"
            )
            return

        # Przywracanie zmiennych stanu gry z wczytanego słownika
        self._level = state["level"]
        self._category = state["category"]
        self.current_word = state["current_word"]
        self.wrong_guesses_counter = state["wrong_guesses_counter"]

        # Konwertujemy listę z JSONa z powrotem na set()
        self.guessed_letters = set(state["guessed_letters"])

        # Wymuszenie aktualizacji interfejsu (GUI), aby pokazać wczytany stan
        self.update_word_display()
        self.update_counter_display()


        QtWidgets.QMessageBox.information(
            self, "Wczytano", "Gra została pomyślnie przywrócona!"
        )

    @QtCore.Slot()
    def on_rules_clicked(self) -> None:
        #Slot wyświetlający okienko z zasadami gry.
        QtWidgets.QMessageBox.information(
            self,
            "Zasady gry",
            "Zasady gry Wisielec:"
        )

    @QtCore.Slot()
    def on_stats_clicked(self) -> None:
        # Tworzymy instancję naszego nowego okna dialogowego
        dialog = StatsDialog(self)
        # .exec() otwiera okno jako "modalne" (blokuje okno główne, dopóki nie zamkniesz statystyk)
        dialog.exec()





    @QtCore.Slot()
    def on_level_changed(self, selected_text: str) -> None:
        # Wymuszenie update GUI, po zmianie poziomu

        self._level = selected_text
        self.button_next_word_click()

    @QtCore.Slot()
    def on_category_changed(self, selected_text: str) -> None:
        # Wymuszenie update GUI, po zmianie kategorii

        self._category = selected_text
        self.button_next_word_click()

    @QtCore.Slot()
    def button_next_word_click(self) -> None:
        self.current_word = self.get_word()[0].upper()

        # resetting single game stats
        self.guessed_letters.clear()
        self.wrong_guesses_counter = 0

        # Display the initial masked word
        self.update_word_display()
        self.update_counter_display()

    def update_word_display(self):
        """Updates your PySide6 text box/label component."""
        # Adjust 'self.text' to whatever your display widget variable name is
        self.text.setText(self.generate_masked_word())

    def generate_masked_word(self) -> str:
        """Converts the current word into a string of underscores and spaces."""
        display_letters = []
        for letter in self.current_word:
            if letter in self.guessed_letters:
                display_letters.append(letter)
            elif letter.isspace() or letter in ["-", "'"]:
                display_letters.append(letter)  # Keep spaces/hyphens visible
            else:
                display_letters.append("_")
        return " ".join(display_letters)

    def update_counter_display(self):
        """Updates a label showing how many mistakes have been made."""
        # Assuming you have a label named 'self.counter_label'
        # self.counter_label.setText(f"Mistakes: {self.wrong_guesses_counter} / {self.max_wrong_guesses}")
        print(f"Mistakes: {self.wrong_guesses_counter}")  # Fallback placeholder


    def keyPressEvent(self, event):
        """PySide6 built-in event handler that intercepts keyboard clicks."""
        # Get the string representation of the pressed key
        key_text = event.text()

        # Ensure it's a valid letter character and not a modifier key like Shift/Ctrl
        if not key_text or not key_text.isalpha():
            super().keyPressEvent(event)
            return

        # Modern UTF-8 safe conversion to uppercase
        guess = key_text.upper()

        # Ignore if the user already guessed this letter
        if guess in self.guessed_letters:
            return

        # Process the new guess
        self.guessed_letters.add(guess)

        if guess in self.current_word:
            # Correct guess! Update the interface text
            self.update_word_display()

            # Check for Win condition (no underscores left)
            if "_" not in self.generate_masked_word():
                self.end_game(won=True)
        else:
            # Wrong guess! Increment counter
            self.wrong_guesses_counter += 1
            self.update_counter_display()

            # Check for Lose condition
            if self.wrong_guesses_counter >= self.max_wrong_guesses:
                self.end_game(won=False)

    def end_game(self, won: bool):
        """Handles win/loss popups."""
        msg = QtWidgets.QMessageBox(self)
        if won:
            msg.setWindowTitle("Gratulacje!")
            msg.setText(f"Wygrałeś! Hasło to: {self.current_word}")
        else:
            msg.setWindowTitle("Koniec Gry")
            msg.setText(f"Przegrałeś. Prawidłowe hasło: {self.current_word}")
        msg.exec()
        self.button_next_word_click()

    def get_word(self) -> tuple[str,int]:
        result: tuple[list[str],int]|None = self._data_manager.get_final_word(self._level, self._category)

        if result is None:
            return f"[Brak haseł dla:\nPoziom: '{self._level}'\nKategoria: '{self._category}']", -1

        return " ".join(result[0]), result[1]


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec())