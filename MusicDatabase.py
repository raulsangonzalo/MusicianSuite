import os
import threading
import time

import numpy
import soundcard as sd

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QMainWindow,
                             QStackedWidget, QSystemTrayIcon, QToolBar,
                             QWidget)
from RecordIdeas import RecordIdeas
from SongList import SongList
from sqliteHandler import createTables


class MusicMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MusicMainWindow, self).__init__(parent)
        self.setWindowTitle("Musician Suite")

        createTables()
        resourcesPath = os.getcwd()
        resourcesPath = os.path.join(resourcesPath, "resources")
        if not os.path.exists(resourcesPath):
            os.mkdir(resourcesPath)

        self.ICON0 = QIcon(QPixmap(os.path.join(resourcesPath, "icon0.png")))
        self.ICON1 = QIcon(QPixmap(os.path.join(resourcesPath, "icon1.png")))

        songList = SongList()
        recordIdeas = RecordIdeas()

        toolBar = QToolBar("title")

        toolBar.addAction(self.ICON0, "Songs")
        toolBar.addAction(self.ICON1, "Record Ideas")

        stackedWidget = QStackedWidget()
        stackedWidget.addWidget(songList)
        stackedWidget.addWidget(recordIdeas)

        toolBar.actionTriggered.connect(self.toolBarActionTriggered)
        self.addToolBar(Qt.TopToolBarArea, toolBar)

        self.setCentralWidget(stackedWidget)

    def toolBarActionTriggered(self, action):
        if action.text() == "Songs":
            self.setCentralWidget(SongList())
        elif action.text() == "Record Ideas":
            self.setCentralWidget(RecordIdeas())
        elif action.text() == "Composition Analysis":
            pass

if __name__ == '__main__':
    app = QApplication([])
    musicMainWindow = MusicMainWindow()
    musicMainWindow.show()
    app.exec()
