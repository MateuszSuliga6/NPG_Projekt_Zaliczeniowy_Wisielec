import sys
from PySide6 import QtCore, QtWidgets
import csv
import random

filename = "data/baza_wisielec.csv"

with open(filename,encoding='utf-8') as f:
    lines = sum(1 for line in f)
def choose_row():
    with open(filename,encoding='utf-8') as f:
        reader = csv.reader(f)
        line_number = random.randrange(lines)
        chosen_row = next(row for row_number, row in enumerate(reader)
                          if row_number == line_number)
        return chosen_row[0].split(";")


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel(" ".join(choose_row()),
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(" ".join(choose_row()))




if __name__ == "__main__":
            app = QtWidgets.QApplication([])
            widget = MyWidget()
            widget.resize(800, 600)
            widget.show()
            widget_list = [widget]
            sys.exit(app.exec())

