import sys
from PySide6 import QtCore, QtWidgets

from data_manager import DataManager

class GameWindow(QtWidgets.QWidget):
    def __init__(self, level: str, category: str) -> None:
        super().__init__()

        self._level: str = level
        self._category: str = category

        self.button_next_word = QtWidgets.QPushButton("Losuj kolejne hasło")

        first_word: str = self.get_word()
        self.text = QtWidgets.QLabel(first_word, alignment=QtCore.Qt.AlignCenter)

        _font = self.text.font()
        _font.setPointSize(24)
        _font.setBold(True)
        self.text.setFont(_font)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button_next_word)

        self.button_next_word.clicked.connect(self.button_next_word_click)

    @QtCore.Slot()
    def button_next_word_click(self):
        self.text.setText(self.get_word())

    def get_word(self) -> str:
        result: str = dm.get_final_word(self._level, self._category)

        if result is None:
            return f"[Brak haseł dla:\nPoziom: '{self._level}'\nKategoria: '{self._category}']"
        slowo = result[0]
        return " ".join(slowo)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    dm = DataManager()

    selected_level: str = "łatwy"
    selected_category: str = "Zwierzęta"

    print(f"Uruchamiam grę dla odczytanych z pliku danych:")
    print(f" - Poziom: '{selected_level}'")
    print(f" - Kategoria: '{selected_category}'")

    widget = GameWindow(level=selected_level, category=selected_category)
    widget.resize(800, 600)
    widget.setWindowTitle(f"Wisielec - {selected_level}: {selected_category}")
    widget.show()

    sys.exit(app.exec())