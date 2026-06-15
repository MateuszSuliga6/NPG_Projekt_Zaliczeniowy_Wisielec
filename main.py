import sys
from PySide6 import QtCore, QtWidgets

from data_manager import DataManager
from Responsive_Widget import ResponsiveBgFrame

class GameWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Wisielec - Gra z interfejsem graficznym")
        self._data_manager = DataManager()

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

        # Tymczasowe wyświetlanie poziom i kategorii -- do usunięcia
        self.label = QtWidgets.QLabel(f"Current Selection: {self._level} {self._category}")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.button_next_word = QtWidgets.QPushButton("Losuj kolejne hasło")

        self.current_word = self.get_word()[0].upper()

        self.guessed_letters = set()
        self.wrong_guesses_counter = 0
        self.max_wrong_guesses = 6

        # Display the initial masked word

        self.text = QtWidgets.QLabel(self.generate_masked_word(), alignment = QtCore.Qt.AlignmentFlag.AlignCenter)

        # Ustawienie głównego okna rozgrywki
        self.main_content = ResponsiveBgFrame("Assets/klasa_latwy.png")
        main_layout = QtWidgets.QVBoxLayout(self.main_content)
        main_layout.addWidget(self.text)

        self.update_counter_display()

        _font = self.text.font()
        _font.setPointSize(24)
        _font.setBold(True)
        self.text.setFont(_font)

        # Ustawienie elementów paska bocznego
        navigation_bar_layout.addWidget(self.button_next_word)
        navigation_bar_layout.addWidget(combo_level)
        navigation_bar_layout.addWidget(combo_category)
        navigation_bar_layout.addWidget(self.label)
        self.button_next_word.clicked.connect(self.button_next_word_click)




        # Ustawianie ułożenia całego okna gry
        master_layout.addWidget(self.main_content)
        master_layout.addWidget(navigation_bar)
        master_layout.addStretch()  # <--- UNCOMMENT THIS LINE

        # --- Line 81: Let the layout know how the labels inside handle spacing ---
        # Right now, your QVBoxLayout(self.main_content) puts self.text in the center.
        # Let's align the text properly so it doesn't try to stretch the parent layout bounds.
        main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        container = QtWidgets.QWidget()
        container.setLayout(master_layout)
        self.setCentralWidget(container)

    @QtCore.Slot()
    def on_level_changed(self, selected_text: str) -> None:
        # Wymuszenie update GUI, po zmianie poziomu
        self.label.setText(f"Current Selection: {selected_text} {self._category}")
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
        self.label.setText(f"Current Selection: {self._level} {selected_text}")
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
            display_letters.append(" ")
        return " ".join(display_letters)

    def update_counter_display(self):
        """Updates a label showing how many mistakes have been made."""
        # Assuming you have a label named 'self.counter_label'
        # self.counter_label.setText(f"Mistakes: {self.wrong_guesses_counter} / {self.max_wrong_guesses}")
        print(f"Mistakes: {self.wrong_guesses_counter}")  # Fallback placeholder
        self.main_content.set_error_count(self.wrong_guesses_counter)


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