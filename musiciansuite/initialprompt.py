from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QHBoxLayout,\
    QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, QSettings
from PyQt5.QtGui import QPixmap, QIcon

import sys
import os

from sqliteHandler import createTables


class InitialPrompt(QDialog):
    databaseSelected = pyqtSignal()

    def __init__(self, parent=None):
        super(InitialPrompt, self).__init__(parent)
        self.init()

    def init(self):
        self._settings = QSettings("Raul Sangonzalo", "Musician Suite")

        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        resourcesPath = os.getcwd()
        resourcesPath = os.path.join(resourcesPath, "resources")
        self.MAIN_ICON = QIcon(os.path.join(resourcesPath, "test.ico"))
        self.setWindowTitle("Musician Suite")
        self.setWindowIcon(self.MAIN_ICON)
        mainLayout = QVBoxLayout(self)
        label = QLabel(
            "<p>Welcome to <b>Musician Suite 0.1b</b>.</p></br> Select an existing database or create a new one.")

        buttonLayout = QHBoxLayout(self)

        newButton = QPushButton("New")
        importButton = QPushButton("Import")

        newButton.clicked.connect(self.createDatabase)
        importButton.clicked.connect(self.importDatabase)

        buttonLayout.addWidget(newButton)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(importButton)

        mainLayout.addWidget(label)
        mainLayout.addLayout(buttonLayout)

    def closeEvent(self, event):
        sys.exit(1)

    def createDatabase(self):  # different handling, so make sure db is appended at the end
        try:
            fileDialog = QFileDialog(filter="SQLite music database (*.db)")
            fileDialog.setAcceptMode(QFileDialog.AcceptSave)
            fileDialog.setDefaultSuffix("db")
            fileDialog.setOptions(QFileDialog.DontUseNativeDialog)
            fileDialog.exec()
            dbName = fileDialog.selectedFiles()
            if dbName[0] != '':
                print(dbName)
                self._settings.setValue("currentDatabase", dbName[0])
                createTables()
                print("yes!")
                self.databaseSelected.emit()
        except Exception as e:
            self._settings.setValue("currentDatabase", None)
            QMessageBox.warning(None, "Error", "%s" % e)

    def importDatabase(self):
        dbName = QFileDialog().getOpenFileName(
            self, filter="SQLite music database (*.db)", options=QFileDialog.DontUseNativeDialog)
        if dbName[0] != '':
            self._settings.setValue("currentDatabase", dbName[0])
            self.databaseSelected.emit()


if __name__ == '__main__':
    app = QApplication([])
    initialPrompt = InitialPrompt()
    initialPrompt.show()
    app.exec()
