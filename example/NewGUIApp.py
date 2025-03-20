import sys
import asyncio
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QInputDialog, QFileDialog,
                             QSplitter, QListWidget, QGraphicsView, QGraphicsScene,
                             QGroupBox, QRadioButton)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor, QDragEnterEvent, QDropEvent, QBrush
from qasync import QEventLoop, asyncSlot
from govee_local_api import GoveeController, GoveeDevice, GoveeLightFeatures
from Audio.audio_loader import load_audio
from Audio.audio_timeline import AudioTimelineView, AudioControlWidget
from Audio.audio_player import AudioPlayer
from Controls import SolidColorControls, SolidSegmentControls, AnimationControls, ColorControls

class LightSequenceItem(QPushButton):  # Inherit from QPushButton for box look
    def __init__(self, name="New Sequence", parent=None):
        super().__init__(name, parent)
        self.name = name
        self.setFixedSize(150, 50)  # Adjust size as needed
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = self.name.encode('utf-8')
            drag.setMimeData(mime_data)
            pixmap = self.grab()  # Use grab to get the button's appearance
            drag.setPixmap(pixmap)
            drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)

class LightSequenceEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor_window = parent
        self.current_pattern_type = None
        self.main_layout = QVBoxLayout(self)
        self.pattern_selection_widget = QWidget()
        self.pattern_selection_layout = QVBoxLayout(self.pattern_selection_widget)
        self.pattern_selection_widget.hide()
        self.current_controls = None

        label = QLabel("Choose Light Pattern Type")
        self.pattern_selection_layout.addWidget(label)

        button_layout = QHBoxLayout()

        self.solid_color_button = QPushButton("Solid Color")
        self.solid_color_button.setFixedSize(150, 80)
        self.solid_color_button.clicked.connect(lambda: self.load_pattern_editor("Solid Color"))
        button_layout.addWidget(self.solid_color_button)

        self.solid_segment_button = QPushButton("Solid Segment")
        self.solid_segment_button.setFixedSize(150, 80)
        self.solid_segment_button.clicked.connect(lambda: self.load_pattern_editor("Solid Segment"))
        button_layout.addWidget(self.solid_segment_button)

        self.animated_button = QPushButton("Animated")
        self.animated_button.setFixedSize(150, 80)
        self.animated_button.clicked.connect(lambda: self.load_pattern_editor("Animated"))
        button_layout.addWidget(self.animated_button)

        self.pattern_selection_layout.addLayout(button_layout)
        self.main_layout.addWidget(self.pattern_selection_widget)

        initial_label = QLabel("Click 'Add New Pattern' to start.")
        self.main_layout.addWidget(initial_label)
        self.current_editor_widget = initial_label

    def show_pattern_selection(self):
        if self.current_editor_widget:
            self.main_layout.removeWidget(self.current_editor_widget)
            self.current_editor_widget.deleteLater()
            self.current_editor_widget = None
            self.current_controls = None
        self.pattern_selection_widget.show()

    def load_pattern_editor(self, pattern_type):
        print(f"Loading editor for: {pattern_type}")
        self.current_pattern_type = pattern_type
        self.pattern_selection_widget.hide()

        if self.current_editor_widget:
            self.main_layout.removeWidget(self.current_editor_widget)
            self.current_editor_widget.deleteLater()
            self.current_editor_widget = None
            self.current_controls = None

        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        back_button = QPushButton("Back to Pattern Selection")
        back_button.clicked.connect(self.show_pattern_selection)
        editor_layout.addWidget(back_button)

        editor_label = QLabel(f"Editing: {pattern_type}")
        editor_layout.addWidget(editor_label)

        # Access the MainWindow instance to get the GoveeDevice
        splitter = self.parent()
        central_widget_ls_editor = splitter.parent() # This is the central widget of LightshowEditorWindow
        lightshow_editor_window = central_widget_ls_editor.parent() # This should be the LightshowEditorWindow
        print(f"LightSequenceEditor - LightshowEditorWindow instance: {lightshow_editor_window}")
        if lightshow_editor_window and hasattr(lightshow_editor_window, 'main_window') and lightshow_editor_window.main_window:
            main_window = lightshow_editor_window.main_window
            print(f"LightSequenceEditor - MainWindow instance: {main_window}")
            govee_device = main_window.device
            print(f"LightSequenceEditor - Govee Device obtained: {govee_device}")
        else:
            print("LightSequenceEditor - Error accessing LightshowEditorWindow or MainWindow")
            return # Exit if we can't get the device

        if pattern_type == "Solid Color":
            self.current_controls = SolidColorControls(govee_device=govee_device)
            editor_layout.addWidget(self.current_controls)
        elif pattern_type == "Solid Segment":
            # Placeholder for getting segment count from Govee API
            segment_count = 12
            self.current_controls = SolidSegmentControls(segment_count=segment_count, govee_device=govee_device)
            editor_layout.addWidget(self.current_controls)
        elif pattern_type == "Animated":
            # Placeholder for getting segment count from Govee API
            segment_count = 12
            # Ensure govee_device is passed here
            self.current_controls = AnimationControls(segment_count=segment_count, govee_device=govee_device)
            editor_layout.addWidget(self.current_controls)

        save_button = QPushButton("Save Sequence")
        save_button.clicked.connect(self.save_sequence)
        editor_layout.addWidget(save_button)

        self.main_layout.addWidget(editor_widget)
        self.current_editor_widget = editor_widget

    def save_sequence(self):
        name = ""
        pattern_data = {}

        if self.current_pattern_type == "Solid Color" and self.current_controls:
            values = self.current_controls.get_values()
            name = values.pop("name")
            pattern_data["type"] = "solid_color"
            pattern_data.update(values)
            print(f"Saving Solid Color: Name={name}, Data={pattern_data}")
        elif self.current_pattern_type == "Solid Segment" and self.current_controls:
            values = self.current_controls.get_values()
            name = values.pop("name")
            pattern_data["type"] = "solid_segment"
            pattern_data.update(values)
            print(f"Saving Solid Segment: Name={name}, Data={pattern_data}")
        elif self.current_pattern_type == "Animated" and self.current_controls:
            values = self.current_controls.get_animation_params()
            name = values.pop("name")
            pattern_data["type"] = "animated"
            pattern_data.update(values)
            print(f"Saving Animated: Name={name}, Data={pattern_data}")

        if name:
            if self.editor_window and self.editor_window.left_section:
                self.editor_window.left_section.add_sequence(name)
                self.show_pattern_selection()

class LightSequenceList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor_window = parent
        layout = QVBoxLayout(self)
        self.add_pattern_button = QPushButton("Add New Pattern")
        self.add_pattern_button.setFixedSize(150, 50) # Match the item size
        self.add_pattern_button.clicked.connect(self.show_pattern_selection_in_editor)
        layout.addWidget(self.add_pattern_button)
        self.list_widget = QListWidget()
        self.list_widget.setDragEnabled(True)
        layout.addWidget(self.list_widget)
        self.setWindowTitle("Saved Sequences")

    def show_pattern_selection_in_editor(self):
        if self.editor_window and self.editor_window.right_section:
            self.editor_window.right_section.show_pattern_selection()

    def add_sequence(self, name):
        item = LightSequenceItem(name)
        list_item = item  # Use the LightSequenceItem directly
        list_widget_item = QWidget() # Dummy widget for layout purposes
        list_layout = QHBoxLayout(list_widget_item)
        list_layout.addWidget(item)
        self.list_widget.addItem(f"")
        self.list_widget.setItemWidget(self.list_widget.item(self.list_widget.count() - 1), list_item)

class LightshowTimeline(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor_window = parent  # Store a reference to the parent window
        self.setAcceptDrops(True)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 1000, 100) # Example size

        # Correct way to set the background brush
        background_color = QColor(50, 50, 50)
        background_brush = QBrush(background_color, Qt.BrushStyle.SolidPattern)
        self.setBackgroundBrush(background_brush)

        self.sequences = [] # Store placed sequences

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().text():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        sequence_name = event.mimeData().text()
        pos = self.mapToScene(event.pos())
        sequence_rect = QRectF(pos.x(), 10, 100, 30) # Example placement
        item = self.scene.addRect(sequence_rect, QColor(100, 100, 255), QColor(200, 200, 255))
        item.setToolTip(sequence_name)
        self.sequences.append({'name': sequence_name, 'rect': sequence_rect})
        event.acceptProposedAction()

class LightshowEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lightshow Editor")
        self.setGeometry(100, 100, 800, 600)
        self.main_window = parent  # Store a reference to the main window

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Section: Saved Light Sequences
        self.left_section = LightSequenceList(self)
        splitter.addWidget(self.left_section)

        # Right Section: Lightshow Template Creator
        self.right_section = LightSequenceEditor(self)
        splitter.addWidget(self.right_section)

        main_layout.addWidget(splitter)

        # Bottom Section: Audio Timeline
        bottom_layout = QVBoxLayout()
        self.timeline_view = LightshowTimeline(self)  # Use your existing LightshowTimeline
        bottom_layout.addWidget(self.timeline_view)

        # Use your existing AudioControlWidget
        self.control_widget = AudioControlWidget()
        bottom_layout.addWidget(self.control_widget)

        self.player = AudioPlayer()

        load_button = QPushButton("Load Audio", self)
        load_button.clicked.connect(self.load_audio_file)
        bottom_layout.addWidget(load_button)

        main_layout.addLayout(bottom_layout)

        # Connect signals from AudioControlWidget to player
        self.control_widget.playClicked.connect(self.player.play)
        self.control_widget.pauseClicked.connect(self.player.pause)
        self.control_widget.stopClicked.connect(self.player.stop)
        self.control_widget.positionChanged.connect(self.player.set_position)

    def load_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Audio File", "", "Audio Files (*.mp3 *.wav)")
        if file_path:
            print(f"Loading audio file: {file_path}")
            # Load audio using the audio loader
            audio_info = load_audio(file_path)  # Use your existing load_audio
            if audio_info:
                self.player.load_audio(audio_info)
                # Update the timeline view with the audio information
                self.timeline_view.set_duration(audio_info['duration'])  # Use your LightshowTimeline's set_duration
                self.control_widget.set_player(self.player)
                self.control_widget.set_audio_data(audio_info) # Pass the audio data to the control widget

            else:
                print("Error loading audio file.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lightshow Maker")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.create_lightshow_button = QPushButton("Create New Lightshow")
        self.create_lightshow_button.clicked.connect(self.open_lightshow_editor)
        layout.addWidget(self.create_lightshow_button)

        self.lightshow_editor_window = None
        self.controller = None
        self.device = None

        self.label = QLabel("Welcome to Lightshow Maker!")
        layout.addWidget(self.label)

        # Keep the Govee control buttons for potential direct control from the main window
        govee_group_layout = QVBoxLayout()
        govee_group_layout.addWidget(QLabel("Govee Control (Optional)"))

        self.look_for_devices_button = QPushButton("Look for devices")
        self.look_for_devices_button.clicked.connect(self.look_for_devices)
        govee_group_layout.addWidget(self.look_for_devices_button)

        self.turn_on_button = QPushButton("Turn Device On")
        self.turn_on_button.clicked.connect(self.turn_device_on)
        govee_group_layout.addWidget(self.turn_on_button)

        self.turn_off_button = QPushButton("Turn Device Off")
        self.turn_off_button.clicked.connect(self.turn_device_off)
        govee_group_layout.addWidget(self.turn_off_button)

        # Added Controls for Debugging
        # Individual animation buttons
        self.test_wave_button = QPushButton("Test Wave")
        self.test_wave_button.clicked.connect(self.test_wave_animation)
        govee_group_layout.addWidget(self.test_wave_button)

        self.test_solid_button = QPushButton("Test Solid")
        self.test_solid_button.clicked.connect(self.test_solid_animation)
        govee_group_layout.addWidget(self.test_solid_button)

        self.set_white_button = QPushButton("Set White")
        self.set_white_button.clicked.connect(self.set_white)
        govee_group_layout.addWidget(self.set_white_button)

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(50)  # Default brightness
        self.brightness_slider.valueChanged.connect(self.set_brightness)
        govee_group_layout.addWidget(QLabel("Brightness:"))
        govee_group_layout.addWidget(self.brightness_slider)

        govee_group_box.setLayout(govee_group_layout)
        layout.addWidget(govee_group_box)


    def open_lightshow_editor(self):
        if not self.lightshow_editor_window or not self.lightshow_editor_window.isVisible():
            self.lightshow_editor_window = LightshowEditorWindow(self) # Pass the main window instance
            self.lightshow_editor_window.show()
        self.lightshow_editor_window.activateWindow()

    def update_device_callback(self, device: GoveeDevice) -> None:
        pass

    def discovered_callback(self, device: GoveeDevice, is_new: bool) -> bool:
        if is_new:
            device.set_update_callback(self.update_device_callback)
        return True

    @asyncSlot()
    async def create_controller(self, discovery_enabled: bool, manual_device_ip: str | None = None) -> GoveeController:
        controller = GoveeController(
            loop=asyncio.get_event_loop(),
            listening_address="10.0.0.15",
            discovery_enabled=discovery_enabled,
            discovered_callback=self.discovered_callback,
            evicted_callback=lambda device: print(f"Evicted {device}"),
        )
        await controller.start()
        if discovery_enabled:
            while not controller.devices:
                print("Waiting for devices... ")
                await asyncio.sleep(1)
        else:
            if not manual_device_ip:
                raise ValueError("Manual device IP must be provided if discovery is disabled.")
            await controller.add_manual_device(manual_device_ip)
            if not controller.devices:
                print(f"No device found at manual IP: {manual_device_ip}")
        if controller.devices:
            self.device = next(iter(controller.devices.values()))
            print(f"Found device: {self.device}")
        else:
            print("No Govee devices found.")
        return controller

    @asyncSlot()
    async def look_for_devices(self):
        if not self.controller:
            self.controller = await self.create_controller(discovery_enabled=True)
        elif not self.controller.is_running():
            await self.controller.start()
        else:
            print("Controller is already running.")

    @asyncSlot()
    async def turn_device_on(self):
        if self.device:
            await self.device.turn_on()
            print(f"Turned on device: {self.device}")
        else:
            print("No device selected to turn on.")

    @asyncSlot()
    async def turn_device_off(self):
        if self.device:
            await self.device.turn_off()
            print(f"Turned off device: {self.device}")
        else:
            print("No device selected to turn off.")

    @asyncSlot()
    async def test_wave_animation(self):
        if self.device:
            animation_params = {
                "color": (255, 0, 0),
                "speed": 120,
                "direction": "left"
            }
            is_animating_flag = lambda: True
            await self.device.start_custom_pattern(pattern_name="Wave", is_animating_flag=is_animating_flag, animation_duration=5, animation_params=animation_params)

        else:
            print("No device selected to test Wave animation.")

    @asyncSlot()
    async def test_solid_animation(self):
        if self.device:
            animation_params = {
                "color": (0, 255, 0),
            }
            is_animating_flag = lambda: True
            await self.device.start_custom_pattern(pattern_name="Solid", is_animating_flag=is_animating_flag, animation_duration=5, animation_params=animation_params)
        else:
            print("No device selected to test Solid animation.")

    @asyncSlot()
    async def set_white(self):
        if self.device:
            await self.device.set_color_temp(2500)
            print(f"Set device {self.device} to white.")
        else:
            print("No device selected to set white.")

    @asyncSlot()
    async def set_brightness(self, brightness):
        if self.device:
            await self.device.set_brightness(brightness)
            print(f"Set brightness of device {self.device} to {brightness}")
        else:
            print("No device selected to set brightness.")


def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    main_window = MainWindow()
    main_window.show()
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    main()
