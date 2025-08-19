# Python Imports
import time

# NXT Imports
import nxt.brick
import nxt.error
import nxt.sensor
import nxt.sensor.generic

# PySide Imports
from PySide6.QtCore import QThread, Signal, QObject

# Project Imports
from sensor.types import SensorType


class SensorThread(QThread):
    distance_signal = Signal(int)

    def __init__(
        self, brick: nxt.brick.Brick, port: nxt.sensor.Port, parent: QObject = None
    ):
        super().__init__(parent=parent)
        self.brick = brick
        self.port = port
        self.sensor_type, self.sensor = self.__detect_sensor(self.brick, self.port)
        # If no sensor was found, dont let this run
        if self.sensor is None:
            self._running = False
        else:
            self._running = True

    def run(self):
        while self._running:
            try:
                dist = self.sensor.get_sample()
                self.distance_signal.emit(dist)
            except Exception:
                self.distance_signal.emit(-1)  # error / no reading
            time.sleep(0.5)

    def stop(self):
        self._running = False

    def __detect_sensor(self, brick: nxt.brick.Brick, port: nxt.sensor.Port):
        """Try to detect what sensor is plugged into a port."""
        try:
            # Try digital/I2C sensor first (like Ultrasonic)
            us = nxt.sensor.generic.Ultrasonic(brick, port)
            us.get_sample()  # if this works, it's ultrasonic
            return SensorType.ULTRASONIC, us
        except nxt.error.I2CError:
            pass

        try:
            # Try touch sensor
            touch = nxt.sensor.generic.Touch(brick, port)
            touch.get_sample()
            return SensorType.TOUCH, touch
        except Exception:
            pass

        try:
            # Try light sensor
            light = nxt.sensor.generic.Light(brick, port)
            light.get_sample()
            return SensorType.LIGHT, light
        except Exception:
            pass

        try:
            # Try sound sensor
            sound = nxt.sensor.generic.Sound(brick, port)
            sound.get_sample()
            return SensorType.SOUND, sound
        except Exception:
            pass

        try:
            # Try color sensor
            color = nxt.sensor.generic.Color(brick, port)
            color.get_sample()
            return SensorType.COLOR, color
        except Exception:
            pass

        return None, None
