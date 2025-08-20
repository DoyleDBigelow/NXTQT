# Python Imports
# NXT Imports
import nxt.brick
import nxt.motor
import nxt.sensor

# PySide Imports
from PySide6.QtWidgets import QWidget, QHBoxLayout, QApplication
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import Qt, QEvent

# Project Imports
from form.controls import Controls
from motor.motor import MotorsController
from motor.types import MotorAction, Power
from sensor.display import SensorDisplay


class Form(QWidget):
    def __init__(self, brick: nxt.brick.Brick):
        super().__init__()
        self.brick = brick
        self.held_keys: set[Qt.Key] = set()
        self.setupBrick()
        self.setupWindow()
        self.createWidgets()
        self.connectEvents()
        self.createLayout()
        QApplication.instance().installEventFilter(self)

    def setupBrick(self):
        self.motor_controller = MotorsController(brick=self.brick, parent=self)
        self.motor_controller.setGoActions(
            motor_actions=[MotorAction(motor_port=nxt.motor.Port.A, power=Power(-100))]
        )
        self.motor_controller.setTurnActions(
            motor_actions=[MotorAction(motor_port=nxt.motor.Port.B, power=Power(25))]
        )

        self.sensor_displays: dict[nxt.sensor.Port, SensorDisplay] = {}
        # Sensor threads
        self.sensor_displays[nxt.sensor.Port.S1] = SensorDisplay(
            brick=self.brick, port=nxt.sensor.Port.S1, parent=self
        )
        self.sensor_displays[nxt.sensor.Port.S2] = SensorDisplay(
            brick=self.brick, port=nxt.sensor.Port.S2, parent=self
        )
        self.sensor_displays[nxt.sensor.Port.S3] = SensorDisplay(
            brick=self.brick, port=nxt.sensor.Port.S3, parent=self
        )
        self.sensor_displays[nxt.sensor.Port.S4] = SensorDisplay(
            brick=self.brick, port=nxt.sensor.Port.S4, parent=self
        )

    def setupWindow(self):
        self.setWindowTitle("NXT Remote Control")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def createWidgets(self):
        self.controls = Controls(self.brick)

    def connectEvents(self):
        pass

    def createLayout(self):
        layout = QHBoxLayout(self)
        self.setLayout(layout)

        layout.addWidget(self.controls)
        for sensor_display in self.sensor_displays.values():
            layout.addWidget(sensor_display)

    def closeEvent(self, event: QCloseEvent):
        for sensor_display in self.sensor_displays.values():
            sensor_display.stopAndDestroyThread()
        event.accept()

    def eventFilter(self, obj, event: QEvent):
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            if event.isAutoRepeat():
                return True

            if event.type() == QEvent.Type.KeyPress:
                self.controls.keyPressed(event.key())
            elif event.type() == QEvent.Type.KeyRelease:
                self.controls.keyReleased(event.key())

            return True  # mark handled (don’t pass to children)
        return super().eventFilter(obj, event)
