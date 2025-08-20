# Python Imports
import time

# NXT Imports
import nxt.brick
import nxt.error
import nxt.sensor
import nxt.sensor.generic

# PySide Imports
from PySide6.QtCore import QThread, Signal, QObject, QTimer

# Project Imports
from sensor.types import SensorType


class SensorWorker(QObject):

    read_signal = Signal(int)

    def __init__(self, sensor: nxt.sensor.Sensor, parent: QObject = None):
        super().__init__(parent=parent)
        self.sensor = sensor
        self._running = False

    def start(self):
        self._running = True
        while self._running:
            self.poll()
            time.sleep(0.1)

    def poll(self):
        try:
            value = self.sensor.get_sample()
            self.read_signal.emit(value)
        except Exception:
            self.read_signal.emit(-1)

    def stop(self):
        self._running = False


class SensorThread(QThread):
    def __init__(self, sensor: nxt.sensor.Sensor, parent=None):
        super().__init__(parent)
        self.worker = SensorWorker(sensor)
        self.worker.moveToThread(self)

        # Connect signals for starting and cleanup
        self.started.connect(self.worker.start)
        self.finished.connect(self.worker.deleteLater)

    def stop(self):
        self.worker.stop()
        self.quit()
        self.wait(500)
