import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_manager import DataManager


class WordsChoosingTest(unittest.TestCase):
    def setUp(self):
            self.dm = DataManager()

    def test_data_loading(self):
        #sprawdenie czy są dostępne poziomy
        self.assertGreater(len(self.dm.get_available_levels()),0, "Błąd odczytu poziomów z pliku CSV!")

    def test_category_logic(self):
        #sprawdzenie czy każdy poziom mam swoje kategorie
        for l in self.dm.get_available_levels():
            self.assertGreater(len(self.dm.get_categories_for_level(l)),0,f"Brak kategori dla poziomu {l}!")

    def test_if_all_sufficient_words_available(self):
        #sprawdzenie czy dla każdej kategori są dostępne wyrazy
        for l in self.dm.get_available_levels():
            for c in self.dm.get_categories_for_level(l):
                self.assertIsNotNone(self.dm.get_final_word(l, c), f"Kategoria {c} nie ma dostępnych wyrazów dla poziomu trudności {l}!")
