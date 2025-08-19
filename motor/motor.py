# Python Imports
import dataclasses
import enum

# NXT Imports
import nxt.brick
import nxt.motor
import nxt.sensor

# PySide Imports
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QCloseEvent

# Project Imports
from motor.types import MotorAction


class MotorsController(QObject):
    def __init__(self, brick: nxt.brick.Brick, parent=None):
        super().__init__(parent)
        self.brick = brick

        self.motors: dict[nxt.motor.Port, nxt.motor.Motor] = {}
        self.motors[nxt.motor.Port.A] = nxt.motor.Motor(
            brick=self.brick, port=nxt.motor.Port.A
        )
        self.motors[nxt.motor.Port.B] = nxt.motor.Motor(
            brick=self.brick, port=nxt.motor.Port.B
        )
        self.motors[nxt.motor.Port.C] = nxt.motor.Motor(
            brick=self.brick, port=nxt.motor.Port.C
        )

        self.go_actions: list[MotorAction] = []
        self.turn_actions: list[MotorAction] = []

    def setGoActions(self, motor_actions: list[MotorAction]):
        self.go_actions = motor_actions

    def setTurnActions(self, motor_actions: list[MotorAction]):
        self.turn_actions = motor_actions

    def goForward(self):
        self.performActions(self.go_actions, invert_power=False)

    def goBackwards(self):
        self.performActions(self.go_actions, invert_power=True)

    def goIdle(self):
        self.performIdle(self.go_actions)

    def goBrake(self):
        self.performBrake(self.go_actions)

    def turnLeft(self):
        self.performActions(self.turn_actions, invert_power=False)

    def turnRight(self):
        self.performActions(self.turn_actions, invert_power=True)

    def turnIdle(self):
        self.performIdle(self.turn_actions)

    def turnBrake(self):
        self.performBrake(self.turn_actions)

    def performActions(
        self, motor_actions: list[MotorAction], invert_power: bool = False
    ):
        for motor_action in motor_actions:
            power = -motor_action.power if invert_power else motor_action.power
            self.motors[motor_action.motor_port].run(power=power, regulated=True)

    def performIdle(self, motor_actions: list[MotorAction]):
        for motor_action in motor_actions:
            self.motors[motor_action.motor_port].idle()

    def performBrake(self, motor_actions: list[MotorAction]):
        for motor_action in motor_actions:
            self.motors[motor_action.motor_port].brake()
