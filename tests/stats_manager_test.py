import unittest
import os
import json
from stats_manager import StatsManager


class TestStatsManager(unittest.TestCase):

    def setUp(self):
        #Utworzenie osobnego pliku dal wyników testowych
        self.manager = StatsManager()
        # Podmieniamy ścieżkę pliku na testową, żeby nie zepsuć prawdziwych statystyk
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_path = os.path.join(self.test_dir, 'data', 'stats_test.json')
        self.manager._full_path = self.test_path
        self.manager._ensure_file_exists()

    def tearDown(self):
        #usunięcie pliku testowych statystyk
        if os.path.exists(self.test_path):
            os.remove(self.test_path)

    def test_ensure_file_exists_creates_default_structure(self):
        #Test czy przy braku pliku tworzy się poprawna domyślna struktura.
        self.assertTrue(os.path.exists(self.test_path))

        with open(self.test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIn("players", data)
        self.assertEqual(data["players"], {})

    def test_save_game_stats_new_player(self):
        #Test czy poprawnie dodaje nowego gracza i zapisuje jego pierwszą grę.
        self.manager.save_game_stats(
            player_name="Tymoteusz", score=50, level="Easy", category="Kino", result=True
        )

        stats = self.manager._read_json()
        self.assertIn("Tymoteusz", stats["players"])
        self.assertEqual(stats["players"]["Tymoteusz"]["games_played"], 1)
        self.assertEqual(stats["players"]["Tymoteusz"]["high_score"], 50)
        self.assertEqual(len(stats["players"]["Tymoteusz"]["history"]), 1)
        self.assertEqual(stats["players"]["Tymoteusz"]["history"][0]["result"], "Won")

    def test_high_score_updates_correctly(self):
        #Test czy rekord punktów jest nadpisywany tylko wtedy, gdy nowy wynik jest większy.
        # Pierwsza gra - słaba
        self.manager.save_game_stats("Tymoteusz", score=30, level="Easy", category="Kino", result=True)
        # Druga gra - życiówka
        self.manager.save_game_stats("Tymoteusz", score=100, level="Hard", category="Kino", result=True)
        # Trzecia gra - gorsza od życiówki
        self.manager.save_game_stats("Tymoteusz", score=45, level="Easy", category="Kino", result=True)

        stats = self.manager._read_json()
        player_data = stats["players"]["Tymoteusz"]

        self.assertEqual(player_data["games_played"], 3)
        self.assertEqual(player_data["high_score"], 100)
        self.assertEqual(player_data["high_score_level"], "Hard")


if __name__ == '__main__':
    unittest.main()