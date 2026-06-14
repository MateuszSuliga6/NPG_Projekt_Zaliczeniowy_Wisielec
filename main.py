import sys
from PySide6 import QtCore, QtWidgets

from data_manager import DataManager

class GameWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.resize(800, 600)
        self.setWindowTitle(f"Wisielec - Gra z interfejsem graficznym")
        self._data_manager = DataManager()

        # Ustalenie layout głównego całego okna
        master_layout = QtWidgets.QVBoxLayout()
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)

        # Ustalenie istnienia paska dolnego i jego formatowania
        # Give it an object name so you can style it with CSS easily
        navigation_bar = QtWidgets.QFrame()
        navigation_bar.setObjectName("Sidebar")
        # Color added for debug, change later
        navigation_bar.setStyleSheet(" background-color: #2c3e50; min-width: 100px; max-height: 100px")

        # Ustalenie layout paska bocznego
        sidebar_layout = QtWidgets.QHBoxLayout(navigation_bar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(15)

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

        first_word: str = self.get_word()
        self.text = QtWidgets.QLabel(first_word, alignment = QtCore.Qt.AlignmentFlag.AlignCenter)

        _font = self.text.font()
        _font.setPointSize(24)
        _font.setBold(True)
        self.text.setFont(_font)

        # Ustalenie elementów paska bocznego
        sidebar_layout.addWidget(self.button_next_word)
        sidebar_layout.addWidget(combo_level)
        sidebar_layout.addWidget(combo_category)
        sidebar_layout.addWidget(self.label)
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
    def on_level_changed(self, selected_text: str) -> None:
        # Wymuszenie update GUI, po zmianie poziomu
        self.label.setText(f"Current Selection: {selected_text} {self._category}")
        self._level = selected_text

    @QtCore.Slot()
    def on_category_changed(self, selected_text: str) -> None:
        # Wymuszenie update GUI, po zmianie kategorii
        self.label.setText(f"Current Selection: {self._level} {selected_text}")
        self._category = selected_text
    @QtCore.Slot()
    def button_next_word_click(self) -> None:
        self.text.setText(self.get_word())

    def get_word(self) -> str:
        result: tuple[list[str],int]|None = self._data_manager.get_final_word(self._level, self._category)

        if result is None:
            return f"[Brak haseł dla:\nPoziom: '{self._level}'\nKategoria: '{self._category}']"
        slowo = result[0]
        return " ".join(slowo)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow()
    window.show()
    sys.exit(app.exec())