import sys
from PySide6 import QtCore, QtWidgets

from data_manager import DataManager

class GameWindow(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Wybór poziomu
        self.combo_level = QtWidgets.QComboBox()
        self.combo_level.addItems(dm.get_available_levels())
        self._level = self.combo_level.currentText()
        self.combo_level.textActivated.connect(self.on_level_changed)

        # Wybór kategorii
        self.combo_category = QtWidgets.QComboBox()
        self.combo_category.addItems(dm.get_categories_for_level(self._level))
        self._category = self.combo_category.currentText()
        self.combo_category.textActivated.connect(self.on_category_changed)

        # tymczasowe wyświetlanie poziom i kategorii
        self.label = QtWidgets.QLabel(f"Current Selection: {self._level}")
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)


        self.button_next_word = QtWidgets.QPushButton("Losuj kolejne hasło")

        first_word: str = self.get_word()
        self.text = QtWidgets.QLabel(first_word, alignment = QtCore.Qt.AlignmentFlag.AlignCenter)

        _font = self.text.font()
        _font.setPointSize(24)
        _font.setBold(True)
        self.text.setFont(_font)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button_next_word)
        self.layout.addWidget(self.combo_level)
        self.layout.addWidget(self.combo_category)
        self.layout.addWidget(self.label)
        self.button_next_word.clicked.connect(self.button_next_word_click)

    @QtCore.Slot()
    def on_level_changed(self, selected_text):
        # Wymuszenie update GUI, po zmianie poziomu
        self.label.setText(f"Current Selection: {selected_text} {self._category}")
        self._level = selected_text

    @QtCore.Slot()
    def on_category_changed(self, selected_text):
        # Wymuszenie update GUI, po zmianie kategorii
        self.label.setText(f"Current Selection: {self._level}{selected_text}")
        self._category = selected_text
    @QtCore.Slot()
    def button_next_word_click(self):
        self.text.setText(self.get_word())

    def get_word(self) -> str:
        result: tuple[list[str],int]|None = dm.get_final_word(self._level, self._category)

        if result is None:
            return f"[Brak haseł dla:\nPoziom: '{self._level}'\nKategoria: '{self._category}']"
        slowo = result[0]
        return " ".join(slowo)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dm = DataManager()

    print(f"Uruchamiam grę dla odczytanych z pliku danych:")

    widget = GameWindow()
    widget.resize(800, 600)
    widget.setWindowTitle(f"Wisielec - Gra z interfejsem graficznym")
    widget.show()

    sys.exit(app.exec())