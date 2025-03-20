from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QStyle)
from PyQt6.QtCore import Qt, pyqtSignal

class AudioControlWidget(QWidget):
    playClicked = pyqtSignal()
    pauseClicked = pyqtSignal()
    stopClicked = pyqtSignal()
    positionChanged = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.player = None
        layout = QHBoxLayout(self)
        self.audio_data = None # Newly Added Line

        # Play Button
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self._toggle_play)
        layout.addWidget(self.play_button)

        # Pause Button
        self.pause_button = QPushButton()
        self.pause_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.pause_button.clicked.connect(self.pauseClicked.emit)
        self.pause_button.setEnabled(False)
        layout.addWidget(self.pause_button)

        # Stop Button
        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.stop_button.clicked.connect(self.stopClicked.emit)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)

        # Current Position Label
        self.position_label = QLabel("0:00")
        layout.addWidget(self.position_label)

        # Duration Label
        self.duration_label = QLabel("0:00")
        layout.addWidget(self.duration_label)

        # Progress Slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(100)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderMoved.connect(self._slider_moved)
        layout.addWidget(self.progress_slider)

    def set_player(self, player):
        self.player = player
        self.player.positionChanged.connect(self._update_ui)
        self.player.playbackStarted.connect(self._update_play_pause_buttons)
        self.player.playbackPaused.connect(self._update_play_pause_buttons)
        self.player.playbackStopped.connect(self._reset_buttons)
        self._update_duration_label()

    def set_audio_data(self, audio_data):  # This is the added method
        """Sets the audio data (time series and sample rate)."""
        self.audio_data = audio_data

    def get_audio_data(self):
        """Returns the audio data."""
        return self.audio_data


    def _toggle_play(self):
        if self.player:
            if self.player.is_playing():
                self.pauseClicked.emit()
            else:
                self.playClicked.emit()

    def _update_ui(self, position):
        minutes = int(position // 60)
        seconds = int(position % 60)
        self.position_label.setText(f"{minutes}:{seconds:02}")
        duration = self.player.get_duration()
        if duration > 0:
            self.progress_slider.setValue(int((position / duration) * 100))

    def _update_duration_label(self):
        if self.player:
            duration = self.player.get_duration()
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            self.duration_label.setText(f"{minutes}:{seconds:02}")

    def _update_play_pause_buttons(self):
        if self.player and self.player.is_playing():
            self.play_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        else:
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.stop_button.setEnabled(self.player and (self.player.get_position() > 0 or self.player.is_playing()))

    def _reset_buttons(self):
        self.play_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.progress_slider.setValue(0)
        self.position_label.setText("0:00")

    def _slider_moved(self, value):
        if self.player:
            duration = self.player.get_duration()
            if duration > 0:
                position = duration * (value / 100.0)
                self.positionChanged.emit(position)
                self.player.set_position(position)

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor, QBrush

class LightshowTimeline(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor_window = parent  # Store a reference to the parent window
        self.setAcceptDrops(True)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 1000, 100) # Example initial size

        # Correct way to set the background brush
        background_color = QColor(50, 50, 50)
        background_brush = QBrush(background_color, Qt.BrushStyle.SolidPattern)
        self.setBackgroundBrush(background_brush)

        self.sequences = [] # Store placed sequences

    def set_duration(self, duration):
        # Update the scene rect based on the audio duration
        self.setSceneRect(0, 0, duration * 10, 100) # Example scaling: 10 pixels per second

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().text():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        sequence_name = event.mimeData().text()
        pos = self.mapToScene(event.pos())
        start_time = pos.x() / 10.0 # Assuming 10 pixels per second
        sequence_duration = 5 # Example duration for the sequence
        sequence_rect = QRectF(pos.x(), 10, sequence_duration * 10, 30) # Example placement
        item = self.scene.addRect(sequence_rect, QColor(100, 100, 255), QColor(200, 200, 255))
        item.setToolTip(f"{sequence_name} (Start: {start_time:.2f}s, Duration: {sequence_duration}s)")
        self.sequences.append({'name': sequence_name, 'start_time': start_time, 'duration': sequence_duration})
        event.acceptProposedAction()
