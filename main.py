import sys
from PySide6 import QtCore, QtWidgets
from Responsive_Widget import ResponsiveBgFrame

from data_manager import DataManager
from stats_manager import StatsManager
from save_manager import SaveManager


class StatsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Twoje Osiągnięcia i Historia")
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
        p_stats = self._stats_manager.get_player_stats("Local player")

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
from Responsive_Widget import ResponsiveBgFrame

class GameWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Wisielec - Gra z interfejsem graficznym")
        self._data_manager = DataManager()
        self._stats_manager = StatsManager()
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

        # Podpięcie sygnałów pod  metody
        self.button_save_game.clicked.connect(self.on_save_game_clicked)
        self.button_load_game.clicked.connect(self.on_load_game_clicked)
        self.button_rules.clicked.connect(self.on_rules_clicked)
        self.button_stats.clicked.connect(self.on_stats_clicked)

        self.button_next_word = QtWidgets.QPushButton("Losuj kolejne hasło")

        self.current_word = self.get_word()[0].upper()

        self.guessed_letters = set()
        self.wrong_guesses_counter = 0
        self.max_wrong_guesses = 6
        self.current_guess = None

        # Ustawienie głównego okna rozgrywki
        self.main_content = ResponsiveBgFrame("Assets/klasa_latwy.png")
        main_layout = QtWidgets.QVBoxLayout(self.main_content)

        # --- FIX: Przekazanie pełnego stanu początkowego do rysowania przez QPainter ---
        self.main_content.set_word_display(self.generate_masked_word())
        self.main_content.set_error_count(self.wrong_guesses_counter)
        self.main_content.set_guessed_letters(self.guessed_letters)
        self.main_content.set_pending_guess(None)

        '''
        main_layout.addWidget(self.text)

        self.update_counter_display()

        _font = self.text.font()
        _font.setPointSize(24)
        _font.setBold(True)
        self.text.setFont(_font)
        '''

        # Ustawienie elementów paska nawigacji
        navigation_bar_layout.addWidget(self.button_next_word)
        navigation_bar_layout.addWidget(combo_level)
        navigation_bar_layout.addWidget(combo_category)

        # Wrzucamy siatkę z 4 przyciskami zamiast starego labela
        navigation_bar_layout.addWidget(buttons_grid_widget)
        self.button_next_word.clicked.connect(self.button_next_word_click)

        # Ustawianie ułożenia całego okna gry
        master_layout.addWidget(self.main_content)
        master_layout.addWidget(navigation_bar)
        master_layout.addStretch()

        main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

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

        # --- FIX: Przekazanie załadowanych danych prosto do warstwy graficznej ---
        self.main_content.set_word_display(self.generate_masked_word())
        self.main_content.set_error_count(self.wrong_guesses_counter)
        self.main_content.set_guessed_letters(self.guessed_letters)
        self.main_content.set_pending_guess(None)

        # Aktualizacja tła dopasowana do wczytanego poziomu trudności
        if self._level == "Łatwy":
            self.main_content.change_image('Assets/klasa_latwy.png')
        elif self._level == "Średni":
            self.main_content.change_image('Assets/klasa_sredni.png')
        elif self._level == "Trudny":
            self.main_content.change_image('Assets/klasa_trudny.png')

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

        if selected_text == "Łatwy" :
            self.main_content.change_image('Assets/klasa_latwy.png')
        elif selected_text == "Średni":
            self.main_content.change_image('Assets/klasa_sredni.png')
        elif selected_text == "Trudny" :
            self.main_content.change_image('Assets/klasa_trudny.png')

        self.button_next_word_click()

    @QtCore.Slot()
    def on_category_changed(self, selected_text: str) -> None:
        # Wymuszenie update GUI, po zmianie kategorii

        self._category = selected_text
        self.button_next_word_click()

    @QtCore.Slot()
    def button_next_word_click(self) -> None:
        self.current_word = self.get_word()[0].upper()
        self.guessed_letters.clear()
        self.wrong_guesses_counter = 0

        # Send the newly cleared empty set to wipe the sprite list clean from the previous match
        self.main_content.set_guessed_letters(self.guessed_letters)

        self.update_word_display()
        self.update_counter_display()

    def update_word_display(self):
        """Redirects game engine calculations into the background widget painter."""
        # Pushes your generated underscores and guessed letters directly to the sprite loop
        self.main_content.set_word_display(self.generate_masked_word())

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
        self.main_content.set_error_count(self.wrong_guesses_counter)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            if self.current_guess is not None:
                guess = self.current_guess
                self.current_guess = None

                # Push None to clear the indicator on screen after confirming
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

        # Push the staged letter to the frame to trigger the painter update!
        self.main_content.set_pending_guess(self.current_guess)

    def process_confirmed_guess(self, guess: str):
        """Evaluates the validated guess against the current hidden word rules."""
        self.guessed_letters.add(guess)

        # PUSH THE UPDATED SET TO THE VIEWPORT GRAPHICS LAYER!
        self.main_content.set_guessed_letters(self.guessed_letters)


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
        # Zabezpieczenie antycheaterkie zwiazane z abusowaniem zapisywania stanu gry
        self._save_manager.delete_save()

        """Obsługuje zapis statystyk do pliku JSON oraz wyświetla pop-up końca gry."""
        total_letters = len(self.guessed_letters)
        correct_letters = total_letters - self.wrong_guesses_counter

        # Wymuszamy zapis na dokładnie ten sam klucz, którego szuka okienko dialogowe
        self._stats_manager.save_game_stats(
            level=self._level,
            category=self._category,
            result=won,
            total_letters_typed=total_letters,
            correct_letters_typed=correct_letters,
            word_text=self.current_word,
            player_name="Local player"  # <--- UPEWNIJ SIĘ, ŻE TO TU JEST
        )

        # Wyświetlenie okienka z informacją o wyniku
        msg = QtWidgets.QMessageBox(self)
        if won:
            msg.setWindowTitle("Gratulacje!")
            msg.setText(f"Wygrałeś! Hasło to: {self.current_word}")
        else:
            msg.setWindowTitle("Koniec Gry")
            msg.setText(f"Przegrałeś. Prawidłowe hasło: {self.current_word}")
        msg.exec()

        # Reset planszy i wylosowanie nowego słowa
        self.button_next_word_click()

    def get_word(self) -> tuple[str,int]:
        result: tuple[list[str],int]|None = self._data_manager.get_final_word(self._level, self._category)

        if result is None:
            return f"[Brak haseł dla:\nPoziom: '{self._level}'\nKategoria: '{self._category}']", -1

        return "".join(result[0]), result[1]

    def resizeEvent(self, event):
        """Intercepts window resize events, forces 2:1 game frame scale,

        and snaps the main window tightly around the content.
        """
        # Call the default behavior first
        super().resizeEvent(event)

        # 1. Determine the active width of the central widget
        current_width = self.centralWidget().width()

        # 2. Calculate the strict 2:1 height for the game artwork
        target_game_height = int(current_width / 2)

        # 3. Lock the game frame to this exact height
        self.main_content.setFixedHeight(target_game_height)

        # 4. Grab the physical height of your bottom navigation bar
        # (It's set to min/max height of 60px in your code, but checking dynamically is safer)
        nav_height = self.findChild(QtWidgets.QFrame, "Navigation_bar").height()

        # 5. The perfect window height is: Game Height + Nav Bar Height + Title Bar/Margins
        # We can calculate this by asking the master layout for its minimum total hint.
        total_content_height = target_game_height + nav_height

        # 6. Force the window framework to match this height exactly.
        # This completely cuts off the trailing dead space!
        self.setFixedHeight(total_content_height)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec())