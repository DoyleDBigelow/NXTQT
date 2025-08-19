# Python Imports
import sys

# NXT Imports
import nxt.locator

# PySide Imports
from PySide6.QtWidgets import QApplication

# Project Imports
from form.form import ControlGUI

if __name__ == "__main__":
    brick = nxt.locator.find(host="00:16:53:11:1C:A9")
    app = QApplication(sys.argv)
    gui = ControlGUI(brick)
    gui.show()
    sys.exit(app.exec())
