import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_menager import DataMenager

#FIX ME
class WordsChoosingTest(unittest.TestCase):
    def setUp(self):
        self.dm = DataMenager()

    def test_data_loading(self):
        #sprawdzenie czy odczytuje plik
        self.assertGreater(len(self.dm._all_words),0, "Błąd odczytu danych z pliku CSV z hasłami!")
        #sprawdenie czy znajduje logikę poziomów
        self.assertGreater(len(self.dm.get_available_levels()),0, "Błąd odczytu poziomów z pliku CSV!")

