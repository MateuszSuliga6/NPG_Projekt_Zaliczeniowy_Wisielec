# -*- coding: utf-8 -*-
import os
import sys

def resolve_path(relative_path: str) -> str:
    """
    Przekierowuje ścieżki względne do tymczasowego katalogu PyInstaller,
    jeśli jest on uruchomiony jako plik wykonywalny.
    """
    if hasattr(sys, '_MEIPASS'):
        # Uruchomienie jako plik wykonywalny
        return os.path.join(sys._MEIPASS, relative_path)

    # Uruchomienie jako skrypt
    return os.path.join(os.path.abspath("."), relative_path)