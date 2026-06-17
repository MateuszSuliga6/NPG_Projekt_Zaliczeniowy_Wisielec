# -*- coding: utf-8 -*-
import os
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from resolve_path import resolve_path

class AudioManager:
    def __init__(self) -> None:
        self.players: dict = {}
        self.outputs = {} # Referencje do wyjść audio
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.audio_dir = resolve_path(os.path.join(base_dir, 'assets', 'audio'))

        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)

    def load_sound(self, name: str, filename: str, volume: float = 0.5) -> None:
        """Wczytanie pliku dźwiękowego (np. .mp3) i przypisanie mu nazwy."""
        path = os.path.join(self.audio_dir, filename)
        if os.path.exists(path):
            # Stworzenie wirtualnego głośnika (AudioOutput) i ustawienie głośność
            output = QAudioOutput()
            output.setVolume(volume)
            
            # Stworzenie odtwarzacz i podpięcie do niego głośnika oraz pliku
            player = QMediaPlayer()
            player.setAudioOutput(output)
            player.setSource(QUrl.fromLocalFile(path))
            
            self.players[name] = player
            self.outputs[name] = output
        else:
            print(f"Brak pliku dźwiękowego: {path}")

    def play(self, name: str) -> None:
        """Odtwarza wczytany dźwięk. Jeśli gra, to przerywa i puszcza od nowa."""
        if name in self.players:
            # Zatrzymanie starego i rozpoczęcie nowego dźwięku
            self.players[name].stop() 
            self.players[name].play()