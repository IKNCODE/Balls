import sys
from PySide6.QtSql import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

SERVER = "DESKTOP-DEQD80G\SQLEXPRESS"
DATABASE = "balls"
USERNAME = ""
PASSWORD = ""

#Connecting to MSSQL SERVER
db = QSqlDatabase.addDatabase('QODBC')
db.setDatabaseName(f'Driver={{SQL SERVER}}; Server={SERVER}; Database={DATABASE}; UID={USERNAME}; PWD={PASSWORD}')
db.open()

class PageLink(QLabel):
    clicked = Signal([str])  # Signal emited when label is clicked

    def __init__(self, text, parent=None):
        super().__init__(text, parent=parent)
        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.setStyleSheet("color: blue;")  # set text color to blue to emulate a link
        self.setCursor(Qt.PointingHandCursor)  # set the cursor to link pointer

    def mousePressEvent(self, event):
        self.clicked.emit(self.text())  # emit the clicked signal when pressed
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

        #last row and data of them
        self.NewIndex = self.v.model().index(self.ds.rowCount() - 1, 0)
        self.maxrow = self.v.model().data(self.NewIndex)
        self.v.hideColumn(0)


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


class ShowAgent(QDialog):
    def __init__(self):
        super().__init__()
        self.initGUI()
        self.hbox = QHBoxLayout()
        vbox = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.page = 0
        self.search = QLineEdit(self)
        self.loaddata()
        query = QSqlQuery("SELECT COUNT(1) FROM Agent")
        while query.next():
            self.maxpage = query.value(0)
        self.plus_button = QPushButton(self.tr("Up"), self)
        self.plus_button.clicked.connect(self.btn_page_up)
        self.save_button = QPushButton(self.tr("Down"), self)
        self.save_button.clicked.connect(self.btn_scroll_down)
        self.hbox.addWidget(self.search)
        self.hbox.addWidget(self.plus_button)
        self.hbox.addWidget(self.save_button)
        vbox.addWidget(self.table)
        vbox.addLayout(self.hbox)

        self.central = QWidget(parent=self)
        self.layout = QVBoxLayout(self.central)
        self.hbox.addWidget(self.central)
        self.hbox.addLayout(self.layout)

        self.combo = QComboBox()
        self.combo.addItems(["Нету", "Наименования (по возр.)","Наименования (по убыв.)","Размер скидки (по возр.)","Размер скидки (по убыв.)","Приоритет (по возр.)","Приоритет (по убыв.)"])
        self.combo.activated[int].connect(self.sorting)
        vbox.addWidget(self.combo)

        self.typeCombo = QComboBox()
        query = QSqlQuery("SELECT Name FROM AgentType")
        self.typeCombo.addItem("Все Типы")
        while query.next():
            self.typeCombo.addItem(query.value(0))
        self.typeCombo.activated[int].connect(self.typeSort)
        vbox.addWidget(self.typeCombo)

        self.pagination(1)

        self.search.textChanged.connect(self.findName)

    def sorting(self, text):
        if text == 1:
            self.table.sortItems(0, Qt.AscendingOrder)
        if text == 2:
            self.table.sortItems(0, Qt.DescendingOrder)
        if text == 11:
            self.table.sortItems(0, Qt.AscendingOrder)
        if text == 12:
            self.table.sortItems(0, Qt.DescendingOrder)
        if text == 5:
            self.table.sortItems(3,Qt.DescendingOrder)
        if text == 6:
            self.table.sortItems(3,Qt.AscendingOrder)

    def typeSort(self, text):
        if text != 0:
            self.table.setRowCount(0)
            sqlquery = QSqlQuery(
                f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType WHERE AgentType.IdType = {text}")
            while sqlquery.next():
                rows = self.table.rowCount()
                self.table.setRowCount(rows + 1)
                self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
                self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
                self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
                self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
            self.table.resizeColumnsToContents()
        else:
            self.loaddata()


    def pagination(self, pagee):
        self.pagination_layout = QHBoxLayout()
        self.offset = int(pagee) - 5
        self.rwcount = int(pagee) + 6
        if self.offset < 1:
            self.offset = 1
        if self.rwcount >= self.maxpage // 5:
            self.rwcount = self.maxpage // 5
        for j in range(self.offset, self.rwcount+1):
            page_link = PageLink(str(j), parent=self)
            self.pagination_layout.addWidget(page_link)
            page_link.clicked.connect(self.switch_page)
        self.layout.addLayout(self.pagination_layout)

    def loaddata(self):
        self.table.setRowCount(0)
        sqlquery = QSqlQuery(f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType Order BY Id_agent Offset 0 Rows Fetch Next 5 Rows Only")
        while sqlquery.next():
            rows = self.table.rowCount()
            self.table.setRowCount(rows + 1)
            self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
            self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
            self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
            self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
        self.table.resizeColumnsToContents()


    def btn_page_up(self):
        if self.page+1 > self.maxpage // 5:
            self.page = self.maxpage // 5
        else:
            self.table.setRowCount(0)
            self.page += 1
            sqlquery = QSqlQuery(f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType Order BY Id_agent Offset {self.page*5} Rows Fetch Next 5 Rows Only")
            while sqlquery.next():
                rows = self.table.rowCount()
                self.table.setRowCount(rows + 1)
                self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
                self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
                self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
                self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
        self.table.resizeColumnsToContents()

    def btn_scroll_down(self):
        if self.page == 0:
            self.page = 0
        else:
            self.table.setRowCount(0)
            self.page -= 1
            sqlquery = QSqlQuery(f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType Order BY Id_agent Offset {self.page*5} Rows Fetch Next 5 Rows Only")
            while sqlquery.next():
                rows = self.table.rowCount()
                self.table.setRowCount(rows + 1)
                self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
                self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
                self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
                self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
        self.table.resizeColumnsToContents()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.delete_data()
        QDialog.keyPressEvent(self, event)

    def switch_page(self, page):
        self.table.setRowCount(0)
        sqlquery = QSqlQuery(f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType Order BY Id_agent Offset {self.page*5} Rows Fetch Next 5 Rows Only")
        while self.pagination_layout.count():
            child = self.pagination_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        while sqlquery.next():
            rows = self.table.rowCount()
            self.table.setRowCount(rows + 1)
            self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
            self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
            self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
            self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
        self.pagination(page)

    def findName(self):
        name = self.search.text().lower()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            # if the search is *not* in the item's text *do not hide* the row
            self.table.setRowHidden(row, name not in item.text().lower())
        if self.search.text == "":
            self.loaddata()

    def initGUI(self):
        self.setWindowTitle("Balls")
        self.setGeometry(300, 300, 1000, 500)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ap = App()
    app.exit()
    sys.exit(app.exec_())