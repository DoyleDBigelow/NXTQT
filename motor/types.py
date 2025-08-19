# Python Imports
import dataclasses

# NXT Imports
import nxt.motor

# PySide Imports

# Project Imports


class Power(int):
    min_val = -100
    max_val = 100

    def __new__(cls, value):
        if not isinstance(value, int):
            raise TypeError("Value must be an int")
        if not (cls.min_val <= value <= cls.max_val):
            raise ValueError(f"Value {value} not in range {cls.min_val}..{cls.max_val}")
        return super().__new__(cls, value)


@dataclasses.dataclass
class MotorAction:
    motor_port: nxt.motor.Port
    power: Power
