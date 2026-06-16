import os
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

class AudioManager:
    def __init__(self):
        self.players = {}
        self.outputs = {} # Musimy trzymać referencje do wyjść audio, inaczej Python je usunie
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_dir = os.path.join(base_dir, 'Assets', 'Audio')

        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)

    def load_sound(self, name: str, filename: str, volume: float = 0.5):
        """Wczytuje plik dźwiękowy (np. .mp3) i przypisuje mu nazwę."""
        path = os.path.join(self.audio_dir, filename)
        if os.path.exists(path):
            # Tworzymy wirtualny głośnik (AudioOutput) i ustawiamy głośność
            output = QAudioOutput()
            output.setVolume(volume)
            
            # Tworzymy odtwarzacz i podpinamy do niego głośnik oraz plik
            player = QMediaPlayer()
            player.setAudioOutput(output)
            player.setSource(QUrl.fromLocalFile(path))
            
            self.players[name] = player
            self.outputs[name] = output
        else:
            print(f"Brak pliku dźwiękowego: {path}")

    def play(self, name: str):
        """Odtwarza wczytany dźwięk. Jeśli gra, to przerywa i puszcza od nowa."""
        if name in self.players:
            # Zatrzymujemy na wypadek, gdyby ktoś klikał bardzo szybko
            self.players[name].stop() 
            self.players[name].play()