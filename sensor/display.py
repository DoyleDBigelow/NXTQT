# Python Imports

# NXT Imports
import nxt.brick
import nxt.error
import nxt.sensor
import nxt.sensor.generic

# PySide Imports
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
)
from PySide6.QtCore import Qt
import qtawesome

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
        self.configureWidgets()
        self.createLayout()
        self.createThread()
        self.connectEvents()
        self.startThread()

    def createWidgets(self):
        self.header = QLabel(f"Port {self.port.value + 1}", parent=self)
        self.restart = QPushButton("", parent=self)
        self.combobox = QComboBox(parent=self)
        self.reading_value = QLabel("", parent=self)
        self.unit = QLabel("", parent=self)

    def configureWidgets(self):
        self.restart.setIcon(qtawesome.icon("fa6s.rotate"))
        self.restart.setToolTip("Reset the sensor connection")

        self.combobox.addItem("None", userData=(None, ""))
        self.combobox.addItem(
            "Ultrasonic", userData=(nxt.sensor.generic.Ultrasonic, "cm")
        )
        self.combobox.addItem("Touch", userData=(nxt.sensor.generic.Touch, ""))
        self.combobox.addItem("Light", userData=(nxt.sensor.generic.Light, "lu"))
        self.combobox.addItem("Color", userData=(nxt.sensor.generic.Color, "rgb"))
        self.combobox.addItem("Sound", userData=(nxt.sensor.generic.Sound, "db"))

    def createLayout(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(3)
        top_layout.addWidget(self.header, alignment=Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(self.restart, alignment=Qt.AlignmentFlag.AlignRight)

        reading_layout = QHBoxLayout()
        reading_layout.setSpacing(3)
        reading_layout.addWidget(
            self.reading_value, alignment=Qt.AlignmentFlag.AlignRight
        )
        reading_layout.addWidget(self.unit, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(top_layout)
        layout.addWidget(self.combobox)
        layout.addLayout(reading_layout)

    def connectEvents(self):
        self.destroyed.connect(self.stopAndDestroyThread)
        self.combobox.currentIndexChanged.connect(self.changeSensor)
        self.restart.clicked.connect(self.recreate)

    def changeSensor(self, _):
        self.recreate()

    def setValue(self, value: str):
        self.reading_value.setText(str(value))

    def createThread(self):
        sensor_class, unit = self.combobox.currentData()

        # If no sensor is selected, simply return
        if sensor_class is None:
            self.unit.setText("")
            return

        try:
            sensor = sensor_class(brick=self.brick, port=self.port)
        # If sensor creation failed, report and return
        except Exception as e:
            print(
                f"Failed to instantiate port {self.port.value} sensor {sensor_class}: {e}"
            )
            self.reading_value.setText("Error")
            self.unit.setText("")
            return

        self.polling_thread = SensorThread(sensor=sensor, parent=self)
        self.polling_thread.worker.read_signal.connect(self.setValue)

        self.unit.setText(unit)

    def stopAndDestroyThread(self):
        try:
            self.polling_thread.worker.read_signal.disconnect()
        except Exception as e:
            pass
        if self.polling_thread is not None:
            self.polling_thread.stop()

    def startThread(self):
        if self.polling_thread is not None:
            try:
                self.polling_thread.start()
            except Exception as e:
                print(f"Failed to start polling thread for port {self.port.value}")
                self.stopAndDestroyThread()
                return

    def recreate(self):
        self.stopAndDestroyThread()
        self.createThread()
        self.startThread()
