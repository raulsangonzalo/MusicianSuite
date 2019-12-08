import os
import threading
import time

import numpy
import soundcard as sd
import sys

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QMainWindow,
                             QShortcut, QStackedWidget, QSystemTrayIcon,
                             QToolBar, QWidget, QMenu, QMessageBox, QLabel, QDialog,
                             QFileDialog)
from recordideas import RecordIdeas
from songlist import SongList
from sqliteHandler import createTables


class MusicMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MusicMainWindow, self).__init__(parent)
        self._settings = QSettings("Raul Sangonzalo", "Musician Suite")
        self.setWindowTitle("Musician Suite")

        resourcesPath = os.getcwd()
        resourcesPath = os.path.join(resourcesPath, "resources")

        self.MAIN_ICON = QIcon(os.path.join(resourcesPath, "test.ico"))
        self.ICON0 = QIcon(QPixmap(os.path.join(resourcesPath, "icon0.png")))
        self.ICON1 = QIcon(QPixmap(os.path.join(resourcesPath, "icon1.png")))
        self.setWindowIcon(self.MAIN_ICON)

        self.fileMenu = QMenu("File")

        self.databaseMenu = QMenu("Database")
        self.databaseMenu.addAction("Create new database")
        self.databaseMenu.addAction("Import database")
        # self.databaseMenu.triggered.connect(self.menuTriggered)

        self.fileMenu.addMenu(self.databaseMenu)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction("Exit")

        self.aboutMenu = QMenu("Help")
        self.aboutMenu.addAction("About")

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.aboutMenu)
        self.menuBar().triggered.connect(self.menuTriggered)

        self.songList = SongList()
        self.recordIdeas = RecordIdeas()

        toolBar = QToolBar("title")

        toolBar.addAction(self.ICON0, "Songs")
        toolBar.addAction(self.ICON1, "Record Ideas")

        # not sure if this is the best way forward
        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.songList)
        self.stackedWidget.addWidget(self.recordIdeas)

        toolBar.actionTriggered.connect(self.toolBarActionTriggered)
        self.addToolBar(Qt.TopToolBarArea, toolBar)

        self.setCentralWidget(self.stackedWidget)

    # quick fix, need better handling of what action is, not text
    def menuTriggered(self, action):
        if action.text() == 'Exit':
            msg = QMessageBox.question(
                None, "Close Application", "Do you want to close the application completely?")
            if msg == QMessageBox.Yes:
                sys.exit(1)
        # same as initial prompt
        elif action.text() == "Create new database":
            fileDialog = QFileDialog(filter="SQLite music database (*.db)")
            fileDialog.setAcceptMode(QFileDialog.AcceptSave)
            fileDialog.setDefaultSuffix("db")
            fileDialog.exec()
            dbName = fileDialog.selectedFiles()
            if dbName[0] != '':
                print(dbName[0])
                self._settings.setValue("currentDatabase", dbName)
                createTables()
                self.songList.populateList()
                self.recordIdeas.populateList()
        # same as initial prompt
        elif action.text() == "Import database":
            dbName = QFileDialog().getOpenFileName(
                self, filter="SQLite music database (*.db)", options=QFileDialog.DontUseNativeDialog)
            if dbName[0] != '':
                print(dbName[0])
                self._settings.setValue("currentDatabase", dbName[0])
                self.songList.populateList()
                self.recordIdeas.populateList()

        elif action.text() == "About":
            self.aboutDialog = QDialog()
            self.aboutDialog.setModal(True)
            self.aboutDialog.setWindowTitle("About")
            self.aboutDialog.setWindowIcon(self.MAIN_ICON)

            text = """<p style="text-align:center;"><b>Musician Suite 0.1 beta</b><br/><br/><br/>Created by Raúl Sangonzalo</p>
                Any bugs of suggestions, you can contact me at<p style="text-ali
                gn:center;"><i>- raulsangonzalo@gmail.com<br/>- github.com/raulsangonzalo/musiciansuite</i></p>
                UI support built with PyQt5<br/>

                Music Player icons made by xnimrodx from www.flaticon.com<br/>
                Other music icons downloaded from https://icons8.com"""
            layout = QHBoxLayout(self.aboutDialog)
            label = QLabel(text)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            layout.addWidget(label)
            self.aboutDialog.show()

    def toolBarActionTriggered(self, action):  # quick fix
        if action.text() == "Songs":
            self.stackedWidget.setCurrentWidget(self.songList)
        elif action.text() == "Record Ideas":
            self.stackedWidget.setCurrentWidget(self.recordIdeas)
        elif action.text() == "Composition Analysis":
            pass

    def closeEvent(self, event):
        event.ignore()  # so app never closes
        self.hide()


if __name__ == '__main__':
    app = QApplication([])
    musicMainWindow = MusicMainWindow()
    musicMainWindow.show()
    app.exec_()
