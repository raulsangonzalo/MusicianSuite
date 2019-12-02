import os
import threading
import time

import numpy
import soundcard as sd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtWidgets import (
    QAction, QApplication, QHBoxLayout, QMainWindow, QStackedWidget,
    QSystemTrayIcon, QToolBar, QWidget, QShortcut)

from recordideas import RecordIdeas
from songlist import SongList
from sqliteHandler import createTables


class MusicMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MusicMainWindow, self).__init__(parent)
        self.setWindowTitle("Musician Suite")

        resourcesPath = os.getcwd()
        resourcesPath = os.path.join(resourcesPath, "resources")

        self.MAIN_ICON = QIcon(os.path.join(resourcesPath, "test.ico"))
        self.ICON0 = QIcon(QPixmap(os.path.join(resourcesPath, "icon0.png")))
        self.ICON1 = QIcon(QPixmap(os.path.join(resourcesPath, "icon1.png")))

        self.songList = SongList()
        self.recordIdeas = RecordIdeas()

        toolBar = QToolBar("title")

        toolBar.addAction(self.ICON0, "Songs")
        toolBar.addAction(self.ICON1, "Record Ideas")

        self.stackedWidget = QStackedWidget() #not sure if this is the best way forward
        self.stackedWidget.addWidget(self.songList)
        self.stackedWidget.addWidget(self.recordIdeas)

        toolBar.actionTriggered.connect(self.toolBarActionTriggered)
        self.addToolBar(Qt.TopToolBarArea, toolBar)

        self.setCentralWidget(self.stackedWidget)

    def startRecordingHook(self):
        print("yeah")
    def toolBarActionTriggered(self, action):
        if action.text() == "Songs":
            self.stackedWidget.setCurrentWidget(self.songList)
        elif action.text() == "Record Ideas":
            self.stackedWidget.setCurrentWidget(self.recordIdeas)
        elif action.text() == "Composition Analysis":
            pass
    def closeEvent(self, event):
        event.ignore()#so app never closes
        self.hide()

if __name__ == '__main__':
    app = QApplication([])
    musicMainWindow = MusicMainWindow()
    musicMainWindow.show()
    app.exec_()
