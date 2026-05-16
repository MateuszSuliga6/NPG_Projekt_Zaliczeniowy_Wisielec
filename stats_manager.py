import json
import os
from datetime import datetime

class StatsManager:
    def __init__(self):
        # Relatywny zapis ścieżek, dla unwersalnosci
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._full_path = os.path.join(base_dir, 'data', 'stats.json')
        self._ensure_file_exists()

    def _read_json(self):
        with open(self._full_path, 'r', encoding = 'utf-8') as json_file:
            return json.load(json_file)

    def _write_json(self, data: dict):
        with open(self._full_path, 'w', encoding = 'utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii = False, indent = 4)
    def _ensure_file_exists(self):
        dir_name = os.path.dirname(self._full_path)

        #sprawdzenie czy jest folder data i ewnetualne utworzenie go
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        #sprawdzenie czy jest plik stats.json i ewenetualne utworzenie go
        if not os.path.exists(self._full_path):
            default_structure = {"players": {}}
            self._write_json(default_structure)

    def save_game_stats(self, player_name: str, score: int, level: str, category: str, result: bool):
        """Zapis statystyk gry danego gracza"""
        #wczytanie aktualnego stanu pliku
        stats = self._read_json()

        #obsługa nowego gracza
        if player_name not in stats["players"]:
            stats["players"][player_name] = {
                "games_played": 0,
                "high_score": 0,
                "high_score_level": "no previous gameplays",
                "high_score_category": "no previous gameplays",
                "history": []
            }
        stats["players"][player_name]["games_played"] += 1
        
        if score > stats["players"][player_name]["high_score"]:
            stats["players"][player_name]["high_score"] = score
            stats["players"][player_name]["high_score_level"] = level
            stats["players"][player_name]["high_score_category"] = category

        game_info = {
            "date" : datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "score" : score,
            "level" : level,
            "category" : category,
            "result": "Won" if result else "Lost"
        }
        #zapis informacji o grze do słownika z historią gier
        stats["players"][player_name]["history"].append(game_info)

        #zapis zmodygikowanego słownika do pliku json
        self._write_json(stats)