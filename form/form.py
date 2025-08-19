# Python Imports
# NXT Imports
import nxt.brick
import nxt.motor
import nxt.sensor

# PySide Imports
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QCloseEvent, QKeyEvent
from PySide6.QtCore import Qt

# Project Imports
from motor.motor import MotorsController
from motor.types import MotorAction, Power
from sensor.thread import SensorThread


class ControlGUI(QWidget):
    def __init__(self, brick: nxt.brick.Brick):
        super().__init__()
        self.brick = brick
        self.held_keys: set[Qt.Key] = set()
        self.setupBrick()
        self.setupWindow()
        self.createWidgets()
        self.connectEvents()
        self.createLayout()
        self.startSensors()

    def setupBrick(self):
        self.motor_controller = MotorsController(brick=self.brick, parent=self)
        self.motor_controller.setGoActions(
            motor_actions=[MotorAction(motor_port=nxt.motor.Port.A, power=Power(-100))]
        )
        self.motor_controller.setTurnActions(
            motor_actions=[MotorAction(motor_port=nxt.motor.Port.B, power=Power(25))]
        )

        self.sensor_threads: dict[nxt.sensor.Port, SensorThread] = {}
        # Sensor threads
        self.sensor_threads[nxt.sensor.Port.S1] = SensorThread(
            brick=self.brick, port=nxt.sensor.Port.S1, parent=self
        )
        self.sensor_threads[nxt.sensor.Port.S2] = SensorThread(
            brick=self.brick, port=nxt.sensor.Port.S2, parent=self
        )
        self.sensor_threads[nxt.sensor.Port.S3] = SensorThread(
            brick=self.brick, port=nxt.sensor.Port.S3, parent=self
        )
        self.sensor_threads[nxt.sensor.Port.S4] = SensorThread(
            brick=self.brick, port=nxt.sensor.Port.S4, parent=self
        )

    def setupWindow(self):
        self.setWindowTitle("NXT Remote Control")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def createWidgets(self):
        self.btn_forward = QPushButton("Forward (W)")

        self.btn_back = QPushButton("Backward (S)")

        self.btn_left = QPushButton("Left (A)")

        self.btn_right = QPushButton("Right (D)")

        self.btn_stop = QPushButton("Stop")

    def connectEvents(self):
        self.btn_forward.pressed.connect(self.motor_controller.goForward)
        self.btn_forward.released.connect(self.motor_controller.goBrake)

        self.btn_back.pressed.connect(self.motor_controller.goBackwards)
        self.btn_back.released.connect(self.motor_controller.goBrake)

        self.btn_left.pressed.connect(self.motor_controller.turnLeft)
        self.btn_left.released.connect(self.motor_controller.turnBrake)

        self.btn_right.pressed.connect(self.motor_controller.turnRight)
        self.btn_right.released.connect(self.motor_controller.turnBrake)

        self.btn_stop.pressed.connect(self.motor_controller.goBrake)
        self.btn_stop.pressed.connect(self.motor_controller.turnBrake)

    def createLayout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.btn_forward)
        layout.addWidget(self.btn_back)
        layout.addWidget(self.btn_left)
        layout.addWidget(self.btn_right)
        layout.addWidget(self.btn_stop)
        self.setLayout(layout)

    def startSensors(self):
        for thread in self.sensor_threads.values():
            thread.start()

    def stopSensors(self):
        for thread in self.sensor_threads.values():
            thread.stop()
            thread.quit()
            thread.wait()

    def closeEvent(self, event: QCloseEvent):
        self.stopSensors()
        self.brick.close()
        event.accept()

    def keyPressEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():  # ignore OS key repeat
            event.accept()
            return
        if event.key() in [
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
        ]:
            self.held_keys.add(event.key())
            self.keys_updated()
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.isAutoRepeat():  # ignore OS key repeat
            event.accept()
            return
        if event.key() in [
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
        ]:
            self.held_keys.discard(event.key())
            self.keys_updated()
        return super().keyReleaseEvent(event)

    def keys_updated(self):
        match Qt.Key.Key_Up in self.held_keys, Qt.Key.Key_Down in self.held_keys:
            case True, True:
                self.motor_controller.goBrake()
            case True, False:
                self.motor_controller.goForward()
            case False, True:
                self.motor_controller.goBackwards()
            case False, False:
                self.motor_controller.goIdle()

        match Qt.Key.Key_Left in self.held_keys, Qt.Key.Key_Right in self.held_keys:
            case True, True:
                self.motor_controller.turnBrake()
            case True, False:
                self.motor_controller.turnLeft()
            case False, True:
                self.motor_controller.turnRight()
            case False, False:
                self.motor_controller.turnIdle()
