import json
import os
from datetime import datetime


class StatsManager:
    def __init__(self):
        # Relatywny zapis ścieżek, dla uniwersalności
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._full_path = os.path.join(base_dir, 'data', 'stats.json')
        self._ensure_file_exists()

    def _read_json(self):
        with open(self._full_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)

    def _write_json(self, data: dict):
        with open(self._full_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)

    def _ensure_file_exists(self):
        dir_name = os.path.dirname(self._full_path)

        # Sprawdzenie czy jest folder data i ewentualne utworzenie go
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # Sprawdzenie czy jest plik stats.json i ewentualne utworzenie go
        if not os.path.exists(self._full_path):
            default_structure = {"players": {}}
            self._write_json(default_structure)

    def save_game_stats(self, level: str, category: str, result: bool,
                        total_letters_typed: int, correct_letters_typed: int, word_text: str, player_name: str = "Local player"):

        stats = self._read_json()

        # Obsługa nowego gracza z nową strukturą pól
        if player_name not in stats["players"]:
            stats["players"][player_name] = {
                "games_played": 0,
                "total_letters": 0,
                "correct_letters": 0,
                "current_win_streak": 0,  # Aktualna seria zwycięstw
                "max_win_streak": 0,  # Rekordowa seria gier bez porażki (high-score serii)
                "won_words_history": [],  # Lista haseł, na których wygrano
                
                # --- NOWE: Waluta i moce dla nowego gracza ---
                "coins": 0,
                "extra_lives": 0,
                "hints": 0
            }

        player = stats["players"][player_name]

        # 1. Aktualizacja ogólnych liczników gier i znaków
        player["games_played"] += 1
        player["total_letters"] += total_letters_typed
        player["correct_letters"] += correct_letters_typed

        # 2. Logika serii zwycięstw (high-score gier bez porażki) i historii wygranych haseł
        if result:  # Jeśli gracz WYGRAŁ
            player["current_win_streak"] += 1
            
            # --- NOWE: Dynamiczna nagroda w postaci monet zależnie od poziomu ---
            if level.lower() == "łatwy":
                player["coins"] += 5
            elif level.lower() == "średni":
                player["coins"] += 10
            elif level.lower() == "trudny":
                player["coins"] += 15
            else:
                player["coins"] += 5  # Domyślna wartość w razie błędu
            
            # Sprawdzenie czy pobito rekord serii bez porażki
            if player["current_win_streak"] > player["max_win_streak"]:
                player["max_win_streak"] = player["current_win_streak"]

            # Dodanie hasła do historii wygranych (tylko jeśli jeszcze go tam nie ma)
            if word_text.upper() not in player["won_words_history"]:
                player["won_words_history"].append(word_text.upper())
        else:  # Jeśli gracz PRZEGRAŁ
            player["current_win_streak"] = 0  # Seria zostaje przerwana

        # Zapis zmodyfikowanego słownika do pliku json
        self._write_json(stats)

    def get_player_stats(self, player_name: str) -> dict | None:
        """Zwraca statystyki gracza wzbogacone o dynamicznie wyliczoną skuteczność."""
        stats = self._read_json()
        players = stats.get("players", {})

        if player_name not in players:
            return None

        player_data = players[player_name].copy()

        # Zabezpieczenie dla starych zapisów, które mogły nie mieć monet
        if "coins" not in player_data:
            player_data["coins"] = 0
            player_data["extra_lives"] = 0
            player_data["hints"] = 0

        # Dynamiczne wyliczanie skuteczności procentowej
        total = player_data["total_letters"]
        correct = player_data["correct_letters"]

        # Zabezpieczenie przed dzieleniem przez zero
        player_data["accuracy_percentage"] = round((correct / total) * 100, 2) if total > 0 else 0.0

        return player_data

    def reset_all_stats(self) -> None:
        default_structure = {"players": {}}
        self._write_json(default_structure)

    def delete_player_stats(self, player_name: str) -> bool:
        stats = self._read_json()

        if player_name in stats["players"]:
            del stats["players"][player_name]
            self._write_json(stats)
            return True

        return False

    # --- NOWE: Funkcja obsługująca sklep ---
    def purchase_item(self, player_name: str, item_type: str, cost: int) -> bool:
        """Odejmuje monety i dodaje przedmiot, jeśli gracza stać. Zwraca True jeśli kupiono."""
        stats = self._read_json()
        
        # Sprawdzamy, czy gracz w ogóle istnieje
        if player_name not in stats["players"]:
            return False
            
        player = stats["players"][player_name]
        
        # Sprawdzamy stan konta i czy przedmiot to faktycznie np. 'extra_lives' lub 'hints'
        if player.get("coins", 0) >= cost and item_type in player:
            player["coins"] -= cost
            player[item_type] += 1
            self._write_json(stats)
            return True
            
        return False