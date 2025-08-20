# Python Imports
import enum


class SensorType(enum.StrEnum):
    ULTRASONIC = enum.auto()
    TOUCH = enum.auto()
    LIGHT = enum.auto()
    SOUND = enum.auto()
    COLOR = enum.auto()
