import sys
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initGUI()


    def initGUI(self):
        