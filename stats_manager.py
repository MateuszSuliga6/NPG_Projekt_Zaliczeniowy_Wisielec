import json
import os

class StatsManager:
    def __init__(self):
        # Relatywny zapis ścieżek, dla unwersalnosci
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self._full_path = os.path.join(base_dir, 'data', 'stats.json')
        self._ensure_file_exists()

    def _read_json(self):
        with open(self._full_path, 'r', encoding = 'utf-8') as json_file:
            return json.load(json_file)

    def _write_json(self, data):
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