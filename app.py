import sys
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

SERVER = "DESKTOP-DEQD80G\SQLEXPRESS"
DATABASE = "balls"
USERNAME = ""
PASSWORD = ""

db = QSqlDatabase.addDatabase('QODBC')
db.setDatabaseName(f'Driver={{SQL SERVER}}; Server={SERVER}; Database={DATABASE}; UID={USERNAME}; PWD={PASSWORD}')
db.open()

#ds = QSqlTableModel()
#ds.setTable('Agent')
#ds.setEditStrategy(QSqlTableModel.OnFieldChange)
#ds.select()

class App(QDialog):
    def __init__(self):
        super().__init__()
        self.initGUI()

        hbox = QHBoxLayout(self)
        vbox = QVBoxLayout(self)

        self.ds = QSqlTableModel()
        self.ds.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.ds.setTable('Agent')
        self.ds.removeColumn(0)
        self.ds.select()
        self.v = QTableView(selectionBehavior=QAbstractItemView.SelectRows)
        self.v.setModel(self.ds)
        self.v.resizeColumnsToContents()


        #self.ds.insertRows(self.ds.rowCount(), 1)

        self.plus_button = QPushButton(self.tr("+"), self)
        self.plus_button.clicked.connect(self.add_data)
        self.plus_button.setShortcut('Ctrl+N')
        self.plus_button.move(50,50)
        self.save_button = QPushButton(self.tr("Save"), self)
        self.save_button.clicked.connect(self.refresh)
        hbox.addWidget(self.v)
        vbox.addWidget(self.plus_button)
        vbox.addWidget(self.save_button)
        hbox.addLayout(vbox)

        self.newadd = QAction('&New',self)
        self.newadd.setShortcut('Ctrl+N')
        self.newadd.triggered.connect(self.accept)



    def initGUI(self):
        self.setWindowTitle("Balls")
        self.setGeometry(300, 300, 1050, 1000)
        self.show()

    @pyqtSlot()
    def add_data(self):
        self.ds.insertRow(self.ds.rowCount())

    @pyqtSlot()
    def refresh(self):
        self.ds.select()

class EditData(QDialog):
    def __init__(self):
        super().__init__()
        self.initGUI()

    def initGUI(self):
        b = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ap = App()
    app.exit()
    sys.exit(app.exec_())