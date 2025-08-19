# Python Imports
# NXT Imports
# PySide Imports
from PySide6.QtWidgets import QFrame

# Project Imports


class VDivider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent, frameShape=QFrame.Shape.VLine, lineWidth=1)
