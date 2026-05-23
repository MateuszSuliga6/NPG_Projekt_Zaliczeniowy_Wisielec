import sys
from PySide6 import QtCore, QtWidgets

from data_manager import DataManager

dm = DataManager()

class MyWidget(QtWidgets.QWidget):
    def __init__(self, poziom, kategoria):
        super().__init__()

        self.poziom = poziom
        self.kategoria = kategoria

        self.button = QtWidgets.QPushButton("Losuj kolejne hasło")

        poczatkowe_slowo = self.pobierz_haslo()
        self.text = QtWidgets.QLabel(poczatkowe_slowo, alignment=QtCore.Qt.AlignCenter)

        czcionka = self.text.font()
        czcionka.setPointSize(24)
        czcionka.setBold(True)
        self.text.setFont(czcionka)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    def pobierz_haslo(self):

        wynik = dm.get_final_word(self.poziom, self.kategoria)

        if wynik is None:
            return f"[Brak haseł dla:\nPoziom: '{self.poziom}'\nKategoria: '{self.kategoria}']"
        slowo = wynik[0]
        return " ".join(slowo)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(self.pobierz_haslo())


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    wybrany_poziom = "łatwy"
    wybrana_kategoria = "Zwierzęta"


    print(f"Uruchamiam grę dla odczytanych z pliku danych:")
    print(f" - Poziom: '{wybrany_poziom}'")
    print(f" - Kategoria: '{wybrana_kategoria}'")

    widget = MyWidget(poziom=wybrany_poziom, kategoria=wybrana_kategoria)
    widget.resize(800, 600)
    widget.setWindowTitle(f"Wisielec - {wybrany_poziom}: {wybrana_kategoria}")
    widget.show()

    sys.exit(app.exec())