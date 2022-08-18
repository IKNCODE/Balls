import sys
from PySide6.QtSql import *
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

SERVER = "DESKTOP-DEQD80G\SQLEXPRESS"
DATABASE = "balls"
USERNAME = ""
PASSWORD = ""

# Connecting to MSSQL SERVER
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
        """redefinition of function that transmit string"""
        self.clicked.emit(self.text())  # emit the clicked signal when pressed
        return super().mousePressEvent(event)


class LoginPage(QDialog):
    def __init__(self):
        super().__init__()
        self.initGUI()

        self.grid = QGridLayout()

        self.login_label = QLabel("Login")
        self.login_field = QLineEdit()
        self.password_label = QLabel("Password")
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Login", self)
        self.login_btn.clicked.connect(self.validation)

        self.grid.setSpacing(10)
        self.grid.addWidget(self.login_label, 1, 0)
        self.grid.addWidget(self.login_field, 1, 1)
        self.grid.addWidget(self.password_label, 2, 0)
        self.grid.addWidget(self.password_field, 2, 1)
        self.grid.addWidget(self.login_btn, 3, 0)

        self.setLayout(self.grid)

    def initGUI(self):
        self.setStyleSheet(
            "QLabel {font: 14pt Comic Sans MS} QPushButton {font: 10pt Comic Sans MS; background-color:#43DCFE}"
            "QLineEdit {font: 10pt Comic Sans MS; background-color:#F9969E } QDialog {background-color:#FFFFFF}")
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Login Page")
        self.setGeometry(300, 300, 500, 300)
        self.show()

    def validation(self):
        """Login function that make transit to another screen"""
        query = QSqlQuery("SELECT login,password,role FROM Users")
        while query.next():
            if self.login_field.text() == query.value(0) and self.password_field.text() == str(query.value(1)):
                if query.value(2) == "admin":
                    _translate = QCoreApplication.translate
                    self.setWindowTitle(_translate("MainWindow", "MainWindow"))
                    app = App()
                    app.exec_()
                elif query.value(2) == "user":
                    _translate = QCoreApplication.translate
                    self.setWindowTitle(_translate("MainWindow", "MainWindow"))
                    shw = ShowAgent()
                    shw.exec_()


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

        # last row and data of them
        self.NewIndex = self.v.model().index(self.ds.rowCount() - 1, 0)
        self.maxrow = self.v.model().data(self.NewIndex)

        # hide agent_id
        self.v.hideColumn(0)

        # adding buttons, and layouts
        self.plus_button = QPushButton(self.tr("+"), self)
        self.plus_button.clicked.connect(self.add_data)
        self.plus_button.setShortcut('Ctrl+N')
        self.plus_button.move(50, 50)
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

        self.newadd = QAction('&New', self)
        self.newadd.setShortcut('Ctrl+N')
        self.newadd.triggered.connect(self.accept)

    def keyPressEvent(self, event):
        # going to func delete_data if user enter "ESC" or "Delete"
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.delete_data()
        QDialog.keyPressEvent(self, event)

    def initGUI(self):
        self.setStyleSheet(
            "QLabel {font: 14pt Comic Sans MS} QPushButton {font: 10pt Comic Sans MS; background-color:#43DCFE} QLineEdit {font: 10pt Comic Sans MS; background-color:#F9969E } QDialog {background-color:#FFFFFF}")

        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Balls")
        self.setGeometry(300, 300, 1000, 500)
        self.show()

    def add_data(self):
        """add row in table"""
        record = self.ds.record()
        # set auto generation for id equals false to avoid errors in sql tables
        record.setGenerated('Id_agent', False)
        self.ds.insertRow(self.ds.rowCount())

    def change(self):
        """switch to another screen"""
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.change_button.setText(_translate("MainWindow", "click me"))
        shwagent = ShowAgent()
        shwagent.exec_()

    def delete_data(self):
        """delete row in table"""
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
        """refresh table (do it after delete/add row in table)"""
        self.ds.select()


class ShowAgent(QDialog):
    def __init__(self):
        super().__init__()
        self.initGUI()
        self.grid = QGridLayout()
        # self.hbox = QHBoxLayout()
        # vbox = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.page = 0
        self.search = QLineEdit(self)
        self.loaddata()

        # calculate row count
        query = QSqlQuery("SELECT COUNT(1) FROM Agent")
        while query.next():
            self.maxpage = query.value(0)

        self.plus_button = QPushButton(self.tr("Up"), self)
        self.plus_button.clicked.connect(self.btn_page_up)
        self.save_button = QPushButton(self.tr("Down"), self)
        self.save_button.clicked.connect(self.btn_scroll_down)

        self.central = QWidget(parent=self)
        self.layout = QVBoxLayout(self.central)

        self.sortText = ""
        self.combo = QComboBox()
        self.combo.addItems(["Нету", "Наименования (по возр.)", "Наименования (по убыв.)", "Размер скидки (по возр.)",
                             "Размер скидки (по убыв.)", "Приоритет (по возр.)", "Приоритет (по убыв.)"])
        self.combo.activated[int].connect(self.sorting)

        self.typeCombo = QComboBox()
        query = QSqlQuery("SELECT Name FROM AgentType")
        self.typeCombo.addItem("Все Типы")
        while query.next():
            self.typeCombo.addItem(query.value(0))
        self.typeCombo.activated[int].connect(self.typeSort)
        # vbox.addWidget(self.typeCombo)

        self.pagination(1)

        self.grid.addWidget(self.search, 1, 0)
        self.grid.addWidget(self.combo, 1, 1)
        self.grid.addWidget(self.typeCombo, 1, 2)
        self.grid.addWidget(self.table, 2, 0, 1, 3)
        self.grid.addWidget(self.plus_button, 3, 0)
        self.grid.addWidget(self.save_button, 3, 1)
        self.grid.addWidget(self.central, 3, 2)

        self.setLayout(self.grid)

        self.search.textChanged.connect(self.findName)

    def sorting(self, text):
        """sort table by name, phone, priority"""
        if text == 1:
            self.table.sortItems(0, Qt.AscendingOrder)
        if text == 2:
            self.table.sortItems(0, Qt.DescendingOrder)
        if text == 11:
            self.table.sortItems(0, Qt.AscendingOrder)
        if text == 12:
            self.table.sortItems(0, Qt.DescendingOrder)
        if text == 5:
            self.table.sortItems(3, Qt.DescendingOrder)
        if text == 6:
            self.table.sortItems(3, Qt.AscendingOrder)

    def typeSort(self, text):
        """sorting table to type"""
        if text != 0:
            self.table.setRowCount(0)
            sqlquery = QSqlQuery(
                f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority, Agent.Logotype FROM Agent JOIN"
                f" AgentType on Agent.AgentType = AgentType.IdType WHERE AgentType.IdType = {text}")
            while sqlquery.next():
                rows = self.table.rowCount()
                self.table.setRowCount(rows + 1)
                self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
                self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
                self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
                self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
                pic = QPixmap(f"agents/{sqlquery.value(4)}")
                pixmap = pic.scaled(49, 70)
                label = QLabel(self)
                label.setPixmap(pixmap)
                label.setScaledContents(True)
                self.table.setCellWidget(rows, 4, label)
            self.table.resizeColumnsToContents()
        else:
            self.loaddata()

    def pagination(self, pagee):
        """add dynamic pagination"""
        self.pagination_layout = QHBoxLayout()
        self.offset = int(pagee) - 5
        self.rwcount = int(pagee) + 6
        if self.offset < 1:
            self.offset = 1
        if self.rwcount >= self.maxpage // 5:
            self.rwcount = self.maxpage // 5
        for j in range(self.offset, self.rwcount + 1):
            page_link = PageLink(str(j), parent=self)
            self.pagination_layout.addWidget(page_link)
            page_link.clicked.connect(self.switch_page)
        self.layout.addLayout(self.pagination_layout)

    def loaddata(self):
        """load data from table witch special columns"""
        self.table.setRowCount(0)
        sqlquery = QSqlQuery(
            f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority, Agent.Logotype FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType Order BY Id_agent Offset 0 Rows Fetch Next 5 Rows Only")
        while sqlquery.next():
            rows = self.table.rowCount()
            self.table.setRowCount(rows + 1)
            self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
            self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
            self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
            self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
            pic = QPixmap(f"agents/{sqlquery.value(4)}")
            pixmap = pic.scaled(49, 70)
            label = QLabel(self)
            label.setPixmap(pixmap)
            label.setScaledContents(True)
            self.table.setCellWidget(rows, 4, label)
        self.table.resizeColumnsToContents()

    def btn_page_up(self):
        if self.page + 1 > self.maxpage // 5:
            self.page = self.maxpage // 5
        else:
            self.table.setRowCount(0)
            self.page += 1
            sqlquery = QSqlQuery(
                f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority, Agent.Logotype FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType Order BY {self.sortText} Id_agent Offset {self.page * 5} Rows Fetch Next 5 Rows Only")
            while sqlquery.next():
                rows = self.table.rowCount()
                self.table.setRowCount(rows + 1)
                self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
                self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
                self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
                self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
                pic = QPixmap(f"agents/{sqlquery.value(4)}")
                pixmap = pic.scaled(49, 70)
                label = QLabel(self)
                label.setPixmap(pixmap)
                label.setScaledContents(True)
                self.table.setCellWidget(rows, 4, label)
        self.combo.setCurrentIndex(0)
        self.table.resizeColumnsToContents()

    def btn_scroll_down(self):
        if self.page == 0:
            self.page = 0
        else:
            self.table.setRowCount(0)
            self.page -= 1
            sqlquery = QSqlQuery(
                f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority, Agent.Logotype FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType Order BY Id_agent Offset {self.page * 5} Rows Fetch Next 5 Rows Only")
            while sqlquery.next():
                rows = self.table.rowCount()
                self.table.setRowCount(rows + 1)
                self.table.setItem(rows, 0, QTableWidgetItem(sqlquery.value(0)))
                self.table.setItem(rows, 1, QTableWidgetItem(sqlquery.value(1)))
                self.table.setItem(rows, 2, QTableWidgetItem(sqlquery.value(2)))
                self.table.setItem(rows, 3, QTableWidgetItem(str(sqlquery.value(3))))
                pic = QPixmap(f"agents/{sqlquery.value(4)}")
                pixmap = pic.scaled(49, 70)
                label = QLabel(self)
                label.setPixmap(pixmap)
                label.setScaledContents(True)
                self.table.setCellWidget(rows, 4, label)
        self.combo.setCurrentIndex(0)
        self.table.resizeColumnsToContents()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            self.delete_data()
        QDialog.keyPressEvent(self, event)

    def switch_page(self, page):
        self.table.setRowCount(0)
        sqlquery = QSqlQuery(
            f"SELECT Agent.Name, AgentType.Name, Agent.Phone, Agent.Priority, Agent.Logotype FROM Agent JOIN AgentType on Agent.AgentType = AgentType.IdType Order BY Id_agent Offset {int(page) * 5} Rows Fetch Next 5 Rows Only")
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
            pic = QPixmap(f"agents/{sqlquery.value(4)}")
            pixmap = pic.scaled(49, 70)
            label = QLabel(self)
            label.setPixmap(pixmap)
            label.setScaledContents(True)
            self.table.setCellWidget(rows, 4, label)
        self.combo.setCurrentIndex(0)
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
        self.setStyleSheet(
            "QLabel {font: 14pt Comic Sans MS} QPushButton {font: 10pt Comic Sans MS; background-color:#43DCFE}"
            "QLineEdit {font: 10pt Comic Sans MS; background-color:#F9969E }"
            "QDialog {background-color:#FFFFFF}")
        self.setWindowIcon(QIcon("icon.png"))
        self.setWindowTitle("Balls")
        self.setGeometry(300, 300, 1000, 500)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ap = LoginPage()
    app.exit()
    sys.exit(app.exec_())
