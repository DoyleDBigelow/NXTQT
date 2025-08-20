# Python Imports

# NXT Imports
import nxt.brick
import nxt.sensor
import nxt.sensor.generic

# PySide Imports
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt

# Project Imports
from sensor.thread import SensorThread
from sensor.types import SensorType


class SensorDisplay(QWidget):
    def __init__(self, brick: nxt.brick.Brick, port: nxt.sensor.Port, parent=None):
        super().__init__(parent)
        self.brick = brick
        self.port = port
        self.polling_thread: SensorThread | None = None
        self.createWidgets()
        self.createLayout()
        self.createThread()
        self.connectEvents()
        self.startThread()

    def createWidgets(self):
        self.header = QLabel(f"Port {self.port.value + 1}")
        self.combobox = QComboBox(parent=self)
        self.combobox.addItem("None", userData=(None, ""))
        self.combobox.addItem(
            "Ultrasonic", userData=(nxt.sensor.generic.Ultrasonic, "cm")
        )
        self.combobox.addItem("Touch", userData=(nxt.sensor.generic.Touch, ""))
        self.combobox.addItem("Light", userData=(nxt.sensor.generic.Light, "lu"))
        self.combobox.addItem("Color", userData=(nxt.sensor.generic.Color, "rgb"))
        self.combobox.addItem("Sound", userData=(nxt.sensor.generic.Sound, "db"))
        self.reading_value = QLabel("", parent=self)
        self.unit = QLabel("", parent=self)

    def createLayout(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        reading_layout = QHBoxLayout()
        reading_layout.setSpacing(3)
        reading_layout.addWidget(
            self.reading_value, alignment=Qt.AlignmentFlag.AlignRight
        )
        reading_layout.addWidget(self.unit, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(self.header, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.combobox)
        layout.addLayout(reading_layout)

    def connectEvents(self):
        self.destroyed.connect(self.stopAndDestroyThread)
        self.combobox.currentIndexChanged.connect(self.changeSensor)

    def changeSensor(self, _):
        self.recreate()

    def setValue(self, value: str):
        self.reading_value.setText(str(value))

    def createThread(self):
        sensor_class, unit = self.combobox.currentData()
        self.unit.setText(unit)
        if sensor_class is None:
            return

        sensor = sensor_class(brick=self.brick, port=self.port)
        self.polling_thread = SensorThread(sensor=sensor, parent=self)
        self.polling_thread.worker.read_signal.connect(self.setValue)

    def stopAndDestroyThread(self):
        try:
            self.polling_thread.worker.read_signal.disconnect()
        except Exception as e:
            pass
        if self.polling_thread is not None:
            self.polling_thread.stop()

    def startThread(self):
        if self.polling_thread is not None:
            self.polling_thread.start()

    def recreate(self):
        self.stopAndDestroyThread()
        self.createThread()
        self.startThread()
