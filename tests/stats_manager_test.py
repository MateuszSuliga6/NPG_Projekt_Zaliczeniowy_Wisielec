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

    def test_save_game_stats_default_local_player(self):
        """Test czy poprawnie dodaje domyślnego gracza 'Local player' i inicjalizuje statystyki."""
        # Wywołujemy zgodnie z nową kolejnością (player_name na końcu, domyślny)
        self.manager.save_game_stats(
            level="Easy",
            category="Kino",
            result=True,
            total_letters_typed=10,
            correct_letters_typed=6,
            word_text="KRAKÓW"
        )

        stats = self.manager._read_json()
        self.assertIn("Local player", stats["players"])

        player_data = stats["players"]["Local player"]
        self.assertEqual(player_data["games_played"], 1)
        self.assertEqual(player_data["total_letters"], 10)
        self.assertEqual(player_data["correct_letters"], 6)
        self.assertEqual(player_data["current_win_streak"], 1)
        self.assertIn("KRAKÓW", player_data["won_words_history"])
        
        # --- NOWE: Sprawdzamy, czy inicjalizują się też monety i moce dla nowych graczy ---
        self.assertIn("coins", player_data)
        self.assertIn("extra_lives", player_data)
        self.assertIn("hints", player_data)

    def test_win_streaks_and_word_history(self):
        """Test czy poprawnie liczy serię wygranych dla Local player i zapisuje historię słów."""
        # 1. Pierwsza wygrana (używamy poprawnej nowej kolejności argumentów)
        self.manager.save_game_stats("Easy", "Kino", True, 8, 5, "BANAN")
        # 2. Druga wygrana (seria powinna wynosić 2)
        self.manager.save_game_stats("Easy", "Kino", True, 10, 6, "KOT")

        stats = self.manager._read_json()
        player_data = stats["players"]["Local player"]
        self.assertEqual(player_data["current_win_streak"], 2)
        self.assertEqual(player_data["max_win_streak"], 2)

        # 3. Porażka (aktualna seria spada do 0, ale max_win_streak zostaje na 2)
        self.manager.save_game_stats("Hard", "Kino", False, 12, 3, "PYTHON")

        stats = self.manager._read_json()
        player_data = stats["players"]["Local player"]
        self.assertEqual(player_data["current_win_streak"], 0)
        self.assertEqual(player_data["max_win_streak"], 2)

        # Sprawdzenie czy w historii słów nie ma hasła z przegranej gry
        self.assertNotIn("PYTHON", player_data["won_words_history"])
        self.assertEqual(len(player_data["won_words_history"]), 2)

    def test_accuracy_percentage_calculation(self):
        """Test czy metoda get_player_stats poprawnie wylicza procent skuteczności dla Local player."""
        self.manager.save_game_stats("Easy", "Kino", True, 20, 15, "TEST")

        # Pobieramy statystyki za pomocą publicznej metody dla naszego profilu
        player_stats = self.manager.get_player_stats("Local player")

        # Oczekiwana skuteczność: (15 / 20) * 100 = 75.0%
        self.assertIsNotNone(player_stats)
        self.assertEqual(player_stats["accuracy_percentage"], 75.0)

    # --- NOWE: Osobny test testujący dynamikę monet i funkcjonowanie sklepu ---
    def test_dynamic_coin_rewards_and_shop(self):
        """Test nagradzania monetami zależnie od poziomu trudności i obsługi zakupów."""
        # Wygrana na Łatwym (+5 monet)
        self.manager.save_game_stats("Łatwy", "Kino", True, 5, 5, "TEST_EASY", "Mati")
        # Wygrana na Średnim (+10 monet)
        self.manager.save_game_stats("Średni", "Kino", True, 5, 5, "TEST_MED", "Mati")
        # Wygrana na Trudnym (+15 monet)
        self.manager.save_game_stats("Trudny", "Kino", True, 5, 5, "TEST_HARD", "Mati")
        
        stats = self.manager._read_json()
        player_data = stats["players"]["Mati"]
        
        # Gracz powinien mieć: 5 + 10 + 15 = 30 monet
        self.assertEqual(player_data["coins"], 30)
        
        # Testujemy udany zakup w sklepie (założenie: życie kosztuje 20)
        success = self.manager.purchase_item("Mati", "extra_lives", 20)
        self.assertTrue(success)
        
        stats_after_purchase = self.manager._read_json()
        self.assertEqual(stats_after_purchase["players"]["Mati"]["coins"], 10)  # Reszta: 30 - 20 = 10
        self.assertEqual(stats_after_purchase["players"]["Mati"]["extra_lives"], 1)  # Wskoczyło 1 życie
        
        # Testujemy próbę zakupu bez środków (założenie: życie kosztuje 20, my mamy 10)
        success_fail = self.manager.purchase_item("Mati", "extra_lives", 20)
        self.assertFalse(success_fail)


if __name__ == '__main__':
    unittest.main()