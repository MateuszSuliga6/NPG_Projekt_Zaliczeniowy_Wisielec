# -*- coding: utf-8 -*-
import os
import json

class SaveManager:
    def __init__(self) -> None :
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._save_path = os.path.join(base_dir, 'data', 'savegame.json')

        os.makedirs(os.path.dirname(self._save_path), exist_ok=True) # Sprawdzenie, że folder data istnieje

    def save_state(self, state_data: dict) -> None:
        """ Zapisuje słownik ze stanem gry do pliku JSON."""
        with open(self._save_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=4)

    def load_state(self) -> dict | None:
        """ Wczytuje stan gry z pliku. Zwraca None, jeśli plik nie istnieje."""
        if not os.path.exists(self._save_path):
            return None
        try:
            with open(self._save_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def delete_save(self) -> None:
        """ Usuwa plik zapisu gry, jeśli istnieje."""
        if os.path.exists(self._save_path):
            try:
                os.remove(self._save_path)
            except Exception:
                pass