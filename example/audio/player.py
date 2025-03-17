import simpleaudio as sa
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

class AudioPlayer(QObject):
    positionChanged = pyqtSignal(float)
    playbackStarted = pyqtSignal()
    playbackPaused = pyqtSignal()
    playbackStopped = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = None
        self.sample_rate = None
        self.play_obj = None
        self.is_playing = False
        self.current_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_position)
        self.timer.setInterval(50)  # Update position every 50 ms

    def load_audio(self, audio_info):
        self.stop()
        self.audio_data = audio_info['audio_data']
        self.sample_rate = audio_info['sample_rate']
        self.current_frame = 0
        self.positionChanged.emit(0.0)

    def play(self):
        if self.audio_data is not None and not self.is_playing:
            audio = (self.audio_data[self.current_frame:] * np.iinfo(np.int16).max).astype(np.int16)
            self.play_obj = sa.play_buffer(
                audio.tobytes(),
                num_channels=1,  # Assuming mono audio
                bytes_per_sample=2,
                sample_rate=self.sample_rate
            )
            self.is_playing = True
            self.timer.start()
            self.playbackStarted.emit()

    def pause(self):
        if self.is_playing and self.play_obj is not None:
            self.play_obj.stop()
            self.is_playing = False
            self.timer.stop()
            self.current_frame += self.play_obj.get_num_frames()
            self.playbackPaused.emit()

    def stop(self):
        if self.play_obj is not None:
            self.play_obj.stop()
        self.is_playing = False
        self.timer.stop()
        self.current_frame = 0
        self.positionChanged.emit(0.0)
        self.playbackStopped.emit()

    def set_position(self, seconds):
        if self.audio_data is not None:
            self.stop()
            self.current_frame = int(seconds * self.sample_rate)
            self.current_frame = max(0, min(self.current_frame, len(self.audio_data)))
            self.positionChanged.emit(seconds)

    def get_position(self):
        if self.audio_data is not None:
            return self.current_frame / self.sample_rate
        return 0.0

    def get_duration(self):
        if self.audio_data is not None:
            return len(self.audio_data) / self.sample_rate
        return 0.0

    def is_playing(self):
        return self.is_playing

    def _update_position(self):
        if self.is_playing and self.play_obj is not None and self.audio_data is not None:
            played_frames = self.play_obj.get_num_frames()
            current_pos_frames = self.current_frame + played_frames
            if current_pos_frames <= len(self.audio_data):
                position_seconds = current_pos_frames / self.sample_rate
                self.positionChanged.emit(position_seconds)
            else:
                self.stop() # Reached end of audio
