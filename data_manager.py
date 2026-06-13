import csv
import random
import os

class DataManager:
    def __init__(self, file_path: str ='data/baza_wisielec.csv') -> None:
        # Relatywny zapis ścieżek, dla unwersalnosci
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._full_path = os.path.join(base_dir, file_path)

        self._all_words = []
        self.load_words()

    def load_words(self) -> None:
        # utf-8 i delimeter związane z polskimi znakami i excelem z którego jest CSV
        with open(self._full_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            self._all_words = list(reader)

    def get_available_levels(self) -> list[str]:
        # Zwraca unikalne poziomy trudności
        levels: list[str] = []
        for row in self._all_words:
            if row['poziom'] not in levels:
                levels.append(row['poziom'])
        return levels

    def get_categories_for_level(self, chosen_level: str) -> list[str]:
        # Filtruje kategorie dostępne tylko dla danego poziomu
        categories: list[str] = []
        for row in self._all_words:
            if row['poziom'] == chosen_level:
                if row['kategoria'] not in categories:
                    categories.append(row['kategoria'])
        return categories

    def get_final_word(self, chosen_level, chosen_category) -> tuple[list[str], int] | None:
        # Losuje hasło spełniające oba warunki
        candidates: list[str] = []
        for row in self._all_words:
            if row['poziom'] == chosen_level and row['kategoria'] == chosen_category:
                candidates.append(row)

        if not candidates:
            return None

        picked_word = random.choice(candidates)
        # Zwraca hasło wraz z długością
        return picked_word['hasło'].upper(), int(picked_word['długość'])
