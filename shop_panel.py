from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon

class HudPanel(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HudPanel")
        
        # styl retro
        self.setStyleSheet("""
            QFrame#HudPanel {
                background-color: #222222; /* Mocny, ciemny panel retro */
                border: 4px solid #000000; /* Gruba, czarna ramka planszy */
            }
            
            /* Styl domyślnych przycisków (np. podpowiedzi i życia) */
            QPushButton {
                background-color: #5c5c5c;
                color: #ffffff;
                /* Wypukła ramka 3D - jasna góra/lewo, ciemny dół/prawo */
                border-top: 3px solid #949494;
                border-left: 3px solid #949494;
                border-bottom: 3px solid #212121;
                border-right: 3px solid #212121;
                padding: 5px;
                font-family: "Courier New", monospace; /* "Kanciasta" retro czcionka */
                font-weight: 900;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #6e6e6e;
            }
            
            /* Wciśnięcie przycisku - odwrócenie cieni na ramce */
            QPushButton:pressed {
                border-top: 3px solid #212121;
                border-left: 3px solid #212121;
                border-bottom: 3px solid #949494;
                border-right: 3px solid #949494;
                padding-top: 7px; /* Imitacja wciśnięcia w dół */
                padding-left: 7px;
            }
            
            QPushButton:disabled {
                background-color: #3b3b3b;
                color: #666666;
                border-top: 3px solid #4f4f4f;
                border-left: 3px solid #4f4f4f;
                border-bottom: 3px solid #1c1c1c;
                border-right: 3px solid #1c1c1c;
            }
        """)

        # Główny układ panelu
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # 1. Przycisk Sklepu (Złoty, wypukły)
        self.btn_shop = QtWidgets.QPushButton("SKLEP")
        self.btn_shop.setStyleSheet("""
            QPushButton {
                background-color: #b87333; /* Miedziany/Złoty */
                color: #ffffff;
                border-top: 3px solid #e09f53;
                border-left: 3px solid #e09f53;
                border-bottom: 3px solid #5c3817;
                border-right: 3px solid #5c3817;
            }
            QPushButton:hover { background-color: #c9803e; }
            QPushButton:pressed {
                border-top: 3px solid #5c3817;
                border-left: 3px solid #5c3817;
                border-bottom: 3px solid #e09f53;
                border-right: 3px solid #e09f53;
                padding-top: 7px; padding-left: 7px;
            }
        """)
        self.btn_shop.setMinimumHeight(45)
        self.btn_shop.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_shop)

        # 2. Napis Ekwipunek
        lbl_eq = QtWidgets.QLabel("MOCE:")
        lbl_eq.setStyleSheet("""
            color: #ecf0f1; 
            font-size: 14px; 
            font-weight: 900; 
            font-family: 'Courier New', monospace;
        """)
        lbl_eq.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_eq)

        # 3. Przycisk Podpowiedzi
        self.btn_hint = QtWidgets.QPushButton("💡 (0)")
        self.btn_hint.setToolTip("Użyj podpowiedzi (odkrywa literę)")
        self.btn_hint.setMinimumHeight(40)
        self.btn_hint.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_hint)

        # 4. Przycisk Dodatkowego Życia
        self.btn_life = QtWidgets.QPushButton("❤️ (0)")
        self.btn_life.setToolTip("Użyj życia (cofa błąd)")
        self.btn_life.setMinimumHeight(40)
        self.btn_life.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.btn_life)

    def update_inventory(self, hints: int, lives: int, errors_count: int):
        self.btn_hint.setText(f"💡 ({hints})")
        self.btn_life.setText(f"❤️ ({lives})")

        self.btn_hint.setEnabled(hints > 0)
        self.btn_life.setEnabled(lives > 0 and errors_count > 0)