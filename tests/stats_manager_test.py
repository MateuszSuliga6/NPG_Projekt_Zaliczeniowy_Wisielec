# test_stats.py
import unittest
import os
import json
from stats_manager import StatsManager


class TestStatsManager(unittest.TestCase):

    def setUp(self):
        """Utworzenie osobnego pliku dla wyników testowych."""
        self.manager = StatsManager()
        # Podmieniamy ścieżkę pliku na testową, żeby nie zepsuć prawdziwych statystyk
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.test_path = os.path.join(self.test_dir, 'data', 'stats_test.json')
        self.manager._full_path = self.test_path
        self.manager._ensure_file_exists()

    def tearDown(self):
        """Usunięcie pliku testowych statystyk po każdym teście."""
        if os.path.exists(self.test_path):
            os.remove(self.test_path)

    def test_ensure_file_exists_creates_default_structure(self):
        """Test czy przy braku pliku tworzy się poprawna domyślna struktura."""
        self.assertTrue(os.path.exists(self.test_path))

        with open(self.test_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertIn("players", data)
        self.assertEqual(data["players"], {})

    def test_save_game_stats_new_player(self):
        """Test czy poprawnie dodaje nowego gracza i inicjalizuje nowe statystyki klawiszy."""
        self.manager.save_game_stats(
            player_name="Tymoteusz",
            level="Easy",
            category="Kino",
            result=True,
            total_letters_typed=10,
            correct_letters_typed=6,
            word_text="KRAKÓW"
        )

        stats = self.manager._read_json()
        self.assertIn("Tymoteusz", stats["players"])

        player_data = stats["players"]["Tymoteusz"]
        self.assertEqual(player_data["games_played"], 1)
        self.assertEqual(player_data["total_letters"], 10)
        self.assertEqual(player_data["correct_letters"], 6)
        self.assertEqual(player_data["current_win_streak"], 1)
        self.assertIn("KRAKÓW", player_data["won_words_history"])

    def test_win_streaks_and_word_history(self):
        """Test czy poprawnie liczy serię wygranych bez porażki i zapisuje unikalne hasła."""
        # 1. Pierwsza wygrana
        self.manager.save_game_stats("Tymoteusz", "Easy", "Kino", True, 8, 5, "BANAN")
        # 2. Druga wygrana (seria powinna wynosić 2)
        self.manager.save_game_stats("Tymoteusz", "Easy", "Kino", True, 10, 6, "KOT")

        stats = self.manager._read_json()
        self.assertEqual(stats["players"]["Tymoteusz"]["current_win_streak"], 2)
        self.assertEqual(stats["players"]["Tymoteusz"]["max_win_streak"], 2)

        # 3. Porażka (aktualna seria spada do 0, ale max_win_streak zostaje na 2)
        self.manager.save_game_stats("Tymoteusz", "Hard", "Kino", False, 12, 3, "PYTHON")

        stats = self.manager._read_json()
        player_data = stats["players"]["Tymoteusz"]
        self.assertEqual(player_data["current_win_streak"], 0)
        self.assertEqual(player_data["max_win_streak"], 2)

        # Sprawdzenie czy w historii słów nie ma hasła z przegranej gry
        self.assertNotIn("PYTHON", player_data["won_words_history"])
        self.assertEqual(len(player_data["won_words_history"]), 2)

    def test_accuracy_percentage_calculation(self):
        """Test czy metoda get_player_stats poprawnie i dynamicznie wylicza procent skuteczności."""
        self.manager.save_game_stats("Tymoteusz", "Easy", "Kino", True, 20, 15, "TEST")

        # Pobieramy statystyki za pomocą publicznej metody
        player_stats = self.manager.get_player_stats("Tymoteusz")

        # Oczekiwana skuteczność: (15 / 20) * 100 = 75.0%
        self.assertIsNotNone(player_stats)
        self.assertEqual(player_stats["accuracy_percentage"], 75.0)


if __name__ == '__main__':
    unittest.main()