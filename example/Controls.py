from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox, QSpinBox,
                             QMessageBox, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from qasync import asyncSlot
import asyncio
import govee_local_api
from Controls import ColorControls  # Assuming ColorControls is in the same directory or package
import animations
from animations import pulse, segmentPulse, wave, implode, explode, breath

class ColorControls(QWidget):
    def __init__(self, label="Color", initial_color="255,255,255", parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel(label + ":")
        self.layout.addWidget(self.label)
        self.color_button = QPushButton()
        self.layout.addWidget(self.color_button)
        self.current_color = self._parse_color_string(initial_color)
        self._update_button_color()
        self.color_button.clicked.connect(self._show_color_dialog)

    def _parse_color_string(self, color_str):
        try:
            r, g, b = map(int, color_str.split(','))
            return QColor(r, g, b)
        except ValueError:
            return QColor(255, 255, 255)

    def _update_button_color(self):
        self.color_button.setStyleSheet(f"background-color: {self.current_color.name()};")

    def _show_color_dialog(self):
        from PyQt6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self._update_button_color()

    def get_color(self):
        return self.current_color.red(), self.current_color.green(), self.current_color.blue()

class SolidColorControls(QWidget):
    def __init__(self, govee_device=None, parent=None):
        super().__init__(parent)
        self.govee_device = govee_device
        layout = QVBoxLayout(self)

        self.name_input = QLineEdit("Solid Color")
        layout.addWidget(self.name_input)

        self.color_controls = ColorControls(label="Color")
        layout.addWidget(self.color_controls)

        self.brightness_spinbox = QSpinBox()
        self.brightness_spinbox.setRange(0, 100)
        self.brightness_spinbox.setValue(50)
        layout.addWidget(QLabel("Brightness:"))
        layout.addWidget(self.brightness_spinbox)

        self.apply_button = QPushButton("Apply Solid Color")
        self.apply_button.clicked.connect(self.apply_solid_color)
        layout.addWidget(self.apply_button)

    def get_values(self):
        color = self.color_controls.get_color()
        return {
            "name": self.name_input.text(),
            "color": color,
            "brightness": self.brightness_spinbox.value()
        }

    @asyncSlot()
    async def apply_solid_color(self):
        if self.govee_device:
            color = self.color_controls.get_color()
            brightness = self.brightness_spinbox.value()
            await self.govee_device.set_color_rgb(color=color)
            await self.govee_device.set_brightness(brightness=brightness)
            print(f"Applied solid color: RGB={color}, Brightness={brightness}")
        else:
            print("Govee device not connected.")

class SolidSegmentControls(QWidget):
    def __init__(self, segment_count, govee_device=None, parent=None):
        super().__init__(parent)
        self.segment_count = segment_count
        self.govee_device = govee_device
        layout = QVBoxLayout(self)

        self.name_input = QLineEdit("Solid Segment")
        layout.addWidget(self.name_input)

        self.segment_index_spinbox = QSpinBox()
        self.segment_index_spinbox.setRange(1, segment_count)
        self.segment_index_spinbox.setValue(1)
        layout.addWidget(QLabel("Segment Index:"))
        layout.addWidget(self.segment_index_spinbox)

        self.color_controls = ColorControls(label="Color")
        layout.addWidget(self.color_controls)

        self.brightness_spinbox = QSpinBox()
        self.brightness_spinbox.setRange(0, 100)
        self.brightness_spinbox.setValue(50)
        layout.addWidget(QLabel("Brightness:"))
        layout.addWidget(self.brightness_spinbox)

        self.apply_button = QPushButton("Test Segment Color")
        self.apply_button.clicked.connect(self.apply_segment_color)
        layout.addWidget(self.apply_button)

    def get_values(self):
        color = self.color_controls.get_color()
        return {
            "name": self.name_input.text(),
            "segment_index": self.segment_index_spinbox.value(),
            "color": color,
            "brightness": self.brightness_spinbox.value()
        }

    @asyncSlot()
    async def apply_segment_color(self):
        if self.govee_device:
            segment_index = self.segment_index_spinbox.value()
            color = self.color_controls.get_color()
            brightness = self.brightness_spinbox.value()
            segments_color = [(0, 0, 0)] * self.segment_count
            segments_color[segment_index - 1] = color
            await self.govee_device.set_segments_color(segments_color)
            await self.govee_device.set_brightness(brightness=brightness)
            print(f"Applied color to segment {segment_index}: RGB={color}, Brightness={brightness}")
        else:
            print("Govee device not connected.")

class AnimationControls(QWidget):
    def __init__(self, segment_count, govee_device=None, parent=None):
        super().__init__(parent)
        self.segment_count = segment_count
        layout = QVBoxLayout(self)
        self.govee_device = govee_device
        self.is_animating = False

        # Name and Duration Input
        name_duration_layout = QHBoxLayout()
        name_layout = QHBoxLayout()
        name_label = QLabel("Name:")
        self.name_input = QLineEdit("Animation Pattern")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        name_duration_layout.addLayout(name_layout)

        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duration (seconds):")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(1, 3600)
        self.duration_spinbox.setValue(10)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spinbox)
        name_duration_layout.addLayout(duration_layout)
        layout.addLayout(name_duration_layout)

        # Animation Type Selection
        self.animation_type_combo = QComboBox()
        self.animation_type_combo.addItems(["Pulse", "Wave", "Implode", "Explode", "Breath", "Segment Pulse"])
        self.animation_type_combo.currentTextChanged.connect(self.update_animation_controls)
        layout.addWidget(self.animation_type_combo)

        # Animation Specific Controls Area
        self.animation_controls_area = QWidget()
        self.animation_controls_layout = QVBoxLayout(self.animation_controls_area)
        layout.addWidget(self.animation_controls_area)

        # Initial setup
        self.setup_pulse_controls()
        self.current_animation = "Pulse"

        # Start/Stop Buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Animation")
        self.start_button.clicked.connect(self.start_animation)
        button_layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop Animation")
        self.stop_button.clicked.connect(self.stop_animation)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.run_next_frame)

    def update_animation_controls(self, animation_type):
        # Clear existing controls
        for i in reversed(range(self.animation_controls_layout.count())):
            widget = self.animation_controls_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.current_animation = animation_type
        if animation_type == "Pulse":
            self.setup_pulse_controls()
        elif animation_type == "Wave":
            self.setup_wave_controls()
        elif animation_type in ["Implode", "Explode"]:
            self.setup_implode_explode_controls()
        elif animation_type == "Breath":
            self.setup_fade_in_out_controls()
        elif animation_type == "Segment Pulse":
            self.setup_segment_pulse_controls()

    def setup_pulse_controls(self):
        # Color Input
        self.pulse_color_controls = ColorControls(label="Pulse Color", initial_color="255,0,0")
        self.animation_controls_layout.addWidget(self.pulse_color_controls)

        # Speed Input
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed (BPM):")
        self.pulse_speed_spinbox = QSpinBox()
        self.pulse_speed_spinbox.setRange(10, 300)
        self.pulse_speed_spinbox.setValue(60)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.pulse_speed_spinbox)
        self.animation_controls_layout.addLayout(speed_layout)

    def setup_wave_controls(self):
        # Color Input
        self.wave_color_controls = ColorControls(label="Wave Color", initial_color="0,255,0")
        self.animation_controls_layout.addWidget(self.wave_color_controls)

        # Speed Input
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        self.wave_speed_spinbox = QSpinBox()
        self.wave_speed_spinbox.setRange(1, 20)
        self.wave_speed_spinbox.setValue(5)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.wave_speed_spinbox)
        self.animation_controls_layout.addLayout(speed_layout)

        # Direction Selection
        direction_layout = QHBoxLayout()
        direction_label = QLabel("Direction:")
        self.wave_direction_combo = QComboBox()
        self.wave_direction_combo.addItems(["Forward", "Backward"])
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.wave_direction_combo)
        self.animation_controls_layout.addLayout(direction_layout)

    def setup_implode_explode_controls(self):
        # Color Input
        self.inout_color_controls = ColorControls(label="Color", initial_color="255,0,255")
        self.animation_controls_layout.addWidget(self.inout_color_controls)

        # Speed Input
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        self.inout_speed_spinbox = QSpinBox()
        self.inout_speed_spinbox.setRange(1, 20)
        self.inout_speed_spinbox.setValue(5)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.inout_speed_spinbox)
        self.animation_controls_layout.addLayout(speed_layout)

    def setup_fade_in_out_controls(self):
        # Color Input
        self.fade_color_controls = ColorControls(label="Color", initial_color="0,0,255")
        self.animation_controls_layout.addWidget(self.fade_color_controls)

        # Speed Input
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        self.fade_speed_spinbox = QSpinBox()
        self.fade_speed_spinbox.setRange(1, 10)
        self.fade_speed_spinbox.setValue(3)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.fade_speed_spinbox)
        self.animation_controls_layout.addLayout(speed_layout)

    def setup_segment_pulse_controls(self):
        # Color Input
        self.segment_pulse_color_controls = ColorControls(label="Pulse Color", initial_color="255,165,0")
        self.animation_controls_layout.addWidget(self.segment_pulse_color_controls)

        # Speed Input
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed (BPM):")
        self.segment_pulse_speed_spinbox = QSpinBox()
        self.segment_pulse_speed_spinbox.setRange(10, 300)
        self.segment_pulse_speed_spinbox.setValue(60)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.segment_pulse_speed_spinbox)
        self.animation_controls_layout.addLayout(speed_layout)

    def get_animation_params(self):
        animation_type = self.animation_type_combo.currentText()
        params = {
            "name": self.name_input.text(),
            "duration": self.duration_spinbox.value(),
            "type": animation_type,
        }
        if animation_type == "Pulse":
            color = self.pulse_color_controls.get_color()
            params["color"] = color if color else (255, 0, 0)
            params["speed"] = self.pulse_speed_spinbox.value()
        elif animation_type == "Wave":
            color = self.wave_color_controls.get_color()
            params["color"] = color if color else (0, 255, 0)
            params["speed"] = self.wave_speed_spinbox.value()
            params["direction"] = self.wave_direction_combo.currentText()
        elif animation_type in ["Implode", "Explode"]:
            color = self.inout_color_controls.get_color()
            params["color"] = color if color else (255, 0, 255)
            params["speed"] = self.inout_speed_spinbox.value()
        elif animation_type == "Breath":
            color = self.fade_color_controls.get_color()
            params["color"] = color if color else (255, 0, 255)
            params["speed"] = self.fade_speed_spinbox.value()
        elif animation_type == "Segment Pulse":
            color = self.segment_pulse_color_controls.get_color()
            params["color"] = color if color else (255, 165, 0)
            params["speed"] = self.segment_pulse_speed_spinbox.value()
        return params

    @asyncSlot()
    async def start_animation(self):
        if self.govee_device and not self.is_animating:
            self.is_animating = True
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            params = self.get_animation_params()
            animation_type = params['type']
            self.animation_duration = params['duration']
            self.animation_start_time = asyncio.get_event_loop().time()
            params['segment_count'] = self.segment_count # Pass segment count to animation functions

            if animation_type == "Pulse":
                self.animation_task = asyncio.create_task(
                    pulse.run_pulse(
                        self.govee_device,
                        params,
                        lambda: self.is_animating,
                        self.animation_duration,
                        self.animation_start_time,
                    )
                )
            elif animation_type == "Wave":
                self.animation_task = asyncio.create_task(
                    wave.run_wave(
                        self.govee_device,
                        params,
                        lambda: self.is_animating,
                        self.animation_duration,
                        self.animation_start_time,
                    )
                )
            elif animation_type == "Implode":
                self.animation_task = asyncio.create_task(
                    implode.run_implode(
                        self.govee_device,
                        params,
                        lambda: self.is_animating,
                        self.animation_duration,
                        self.animation_start_time,
                    )
                )
            elif animation_type == "Explode":
                self.animation_task = asyncio.create_task(
                    explode.run_explode(
                        self.govee_device,
                        params,
                        lambda: self.is_animating,
                        self.animation_duration,
                        self.animation_start_time,
                    )
                )
            elif animation_type == "Breath":
                self.animation_task = asyncio.create_task(
                    breath.run_breath(
                        self.govee_device,
                        params,
                        lambda: self.is_animating,
                        self.animation_duration,
                        self.animation_start_time,
                    )
                )
            elif animation_type == "Segment Pulse":
                self.animation_task = asyncio.create_task(
                    segmentPulse.run_segment_pulse(
                        self.govee_device,
                        params,
                        lambda: self.is_animating,
                        self.animation_duration,
                        self.animation_start_time,
                    )
                )
        elif not self.govee_device:
            QMessageBox.warning(self, "Animation", "Govee device not connected.")
        elif self.is_animating:
            QMessageBox.warning(self, "Animation", "Animation is already running.")

    def stop_animation(self):
        self.is_animating = False
        if hasattr(self, 'animation_task') and self.animation_task:
            self.animation_task.cancel()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
