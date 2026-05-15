import csv
import random
import os


class DataManager:
    def __init__(self, file_path='data/baza_wisielec.csv'):
        # Inicjalizacja ścieżki
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._full_path = os.path.join(base_dir, file_path)

        # Pusta lista na start
        self._all_words = []

        # Wczytujemy dane
        self.load_words()

    def load_words(self):

        file = open(self._full_path, mode='r', encoding='utf-8')
        reader = csv.DictReader(file, delimiter=';')
        self._all_words = list(reader)
        file.close()
        print(f"Wczytano słowa. Liczba rekordów: {len(self._all_words)}")

    def get_available_levels(self):
        """Zwraca unikalne poziomy trudności."""
        levels = []
        for row in self._all_words:
            if row['poziom'] not in levels:
                levels.append(row['poziom'])
        return levels

    def get_categories_for_level(self, chosen_level):
        """Filtruje kategorie dostępne tylko dla danego poziomu."""
        categories = []
        for row in self._all_words:
            if row['poziom'] == chosen_level:
                if row['kategoria'] not in categories:
                    categories.append(row['kategoria'])
        return categories

    def get_final_word(self, chosen_level, chosen_category):
        """Losuje hasło spełniające oba warunki."""
        candidates = []
        for row in self._all_words:
            if row['poziom'] == chosen_level and row['kategoria'] == chosen_category:
                candidates.append(row)

        if not candidates:
            return None

        picked_word = random.choice(candidates)
        """Zwraca hasło - długość"""
        return (picked_word['hasło'].upper(), int(picked_word['długość']))

"""Sprawdzenie czy działa poprawnie"""

if __name__ == "__main__":
    dm = DataManager()

    lvls = dm.get_available_levels()
    print("Dostępne poziomy:", lvls)

    if lvls:
        test_lvl = lvls[0]
        categories = dm.get_categories_for_level(test_lvl)
        print(f"Kategorie dla {test_lvl}:", categories)

        if categories:
            chosen_category = categories[0]
            word, length = dm.get_final_word(test_lvl, chosen_category)
            print(f"Wylosowano: {word} (litery: {length})")