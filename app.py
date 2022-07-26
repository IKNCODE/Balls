import sys
from PySide6.QtSql import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

SERVER = "DESKTOP-DEQD80G\SQLEXPRESS"
DATABASE = "balls"
USERNAME = ""
PASSWORD = ""

db = QSqlDatabase.addDatabase('QODBC')
db.setDatabaseName(f'Driver={{SQL SERVER}}; Server={SERVER}; Database={DATABASE}; UID={USERNAME}; PWD={PASSWORD}')
db.open()

class PageLink(QLabel):

    clicked = Signal([str])  # Signal emited when label is clicked

    def __init__(self, text, parent=None):
        super().__init__(text, parent=parent)
        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.setStyleSheet("color: blue;") # set text color to blue to emulate a link
        self.setCursor(Qt.PointingHandCursor)  # set the cursor to link pointer

    def mousePressEvent(self, event):
        self.clicked.emit(self.text())   # emit the clicked signal when pressed
        return super().mousePressEvent(event)


class App(QDialog):
    def __init__(self):
        super().__init__()
        self.initGUI()

        hbox = QHBoxLayout(self)
        vbox = QVBoxLayout(self)

        self.ds = QSqlTableModel()
        self.ds.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.ds.setTable('Agent')
        self.ds.select()
        self.v = QTableView(selectionBehavior=QAbstractItemView.SelectRows)
        self.v.setModel(self.ds)
        self.v.resizeColumnsToContents()

        self.NewIndex = self.v.model().index(self.ds.rowCount() - 1, 0)
        self.maxrow = self.v.model().data(self.NewIndex)

        self.v.hideColumn(0)

        #self.ds.insertRows(self.ds.rowCount(), 1)

        self.plus_button = QPushButton(self.tr("+"), self)
        self.plus_button.clicked.connect(self.add_data)
        self.plus_button.setShortcut('Ctrl+N')
        self.plus_button.move(50,50)
        self.save_button = QPushButton(self.tr("Save"), self)
        self.save_button.clicked.connect(self.refresh)
        self.delete_button = QPushButton(self.tr("Delete"), self)
        self.delete_button.clicked.connect(self.delete_data)
        self.change_button = QPushButton(self.tr("To User"), self)
        self.change_button.clicked.connect(self.change)
        hbox.addWidget(self.v)
        vbox.addWidget(self.plus_button)
        vbox.addWidget(self.save_button)
        vbox.addWidget(self.delete_button)
        vbox.addWidget(self.change_button)
        hbox.addLayout(vbox)

        self.newadd = QAction('&New',self)
        self.newadd.setShortcut('Ctrl+N')
        self.newadd.triggered.connect(self.accept)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.delete_data()
        QDialog.keyPressEvent(self, event)

    def initGUI(self):
        self.setWindowTitle("Balls")
        self.setGeometry(300, 300, 1000, 500)
        self.show()

    def add_data(self):
        record = self.ds.record()
        record.setGenerated('Id_agent', False)
        self.ds.insertRow(self.ds.rowCount())

    def change(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.change_button.setText(_translate("MainWindow", "click me"))
        shwagent = ShowAgent()
        shwagent.exec_()

    def delete_data(self):
            if self.v.selectionModel().hasSelection():
                indexes = [QPersistentModelIndex(index) for index in self.v.selectionModel().selectedRows()]
                print(self.maxrow)
                next_ix = QPersistentModelIndex(self.ds.index(self.maxrow + 1, 0))
                for index in indexes:
                    print('Deleting row %d...' % index.row())
                    self.ds.removeRow(index.row())

                self.v.setCurrentIndex(QModelIndex(next_ix))
            else:
                print('No row selected!')

    def refresh(self):
        self.ds.select()


class ShowAgent(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initGUI()

        self.ds = QSqlTableModel()
        self.ds.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.ds.setTable('Agent')

        self.ds.select()
        self.v = QTableView(selectionBehavior=QAbstractItemView.SelectRows)
        self.v.setModel(self.ds)
        self.v.resizeColumnsToContents()

        self.NewIndex = self.v.model().index(self.ds.rowCount() - 1, 0)
        self.maxrow = self.v.model().data(self.NewIndex)

        self.v.hideColumn(0)
        self.central = QWidget(parent=self)
        self.layout = QVBoxLayout(self.central)
        self.setCentralWidget(self.central)

        # create the stacked widget that will contain each page...
        self.stackWidget = QStackedWidget(parent=self)
        self.layout.addWidget(self.stackWidget)

        # setup the layout for the page numbers below the stacked widget
        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.addStretch(0)
        self.pagination_layout.addWidget(QLabel("<"))

        data = []
        for b in range(0, (self.ds.rowCount() + 1 - 90)):
            data.append([])
            for j in range(7):
                index = self.ds.index(b, j)
                # We suppose data are strings
                data[b].append(str(self.ds.data(index)))
                print(data)
        # create pages and corresponding labels
        page = 1

        rwcount = page * 10
        self.offset = (page-1)*rwcount
        self.ds.select()


        #self.layout.addWidget(self.v)


        for i in range(1, (self.ds.rowCount() + 1 - 90)):
                page_link = PageLink(str(i), parent=self)
                self.pagination_layout.addWidget(page_link)
                page = QWidget()
                gg = QVBoxLayout(page)
                layout = QVBoxLayout(page)
                label_id = QLabel(str(data[i-1][0]))
                label_name = QLabel(str(data[i-1][1]))
                label_type = QLabel(str(data[i-1][2]))
                label_inn = QLabel(str(data[i-1][3]))
                gg.addWidget(label_id)
                gg.addWidget(label_name)
                gg.addWidget(label_type)
                gg.addWidget(label_inn)
                gg.setContentsMargins(0, 1, 0, 0)
                layout.addLayout(gg)
                self.stackWidget.addWidget(page)
                page_link.clicked.connect(self.switch_page)
        self.pagination_layout.addWidget(QLabel(">"))
        self.layout.addLayout(self.pagination_layout)

    def initGUI(self):
        self.setWindowTitle("Balls")
        self.setGeometry(300, 300, 1000, 500)
        self.show()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.delete_data()
        QDialog.keyPressEvent(self, event)

    def switch_page(self, page):
        self.stackWidget.setCurrentIndex(int(page) - 1)
        self.offset+=1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ap = App()
    app.exit()
    sys.exit(app.exec_())