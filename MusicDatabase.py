from PyQt5.QtWidgets import QMainWindow, QApplication, QToolBar, QAction, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

import soundcard as sd
import numpy
import pyaudio
import wavio
import time
import threading

global enable
enable = True

from SongList import SongList
from RecordIdeas import RecordIdeas

class MusicMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MusicMainWindow, self).__init__(parent)
        window = QWidget()
        mainHorizontalLayout = QHBoxLayout(self)
        #songList = SongList()
        #recordIdeas = RecordIdeas()

        
        toolBar = QToolBar("title")
        toolBar.addAction("Songs")
        toolBar.addAction("Record Ideas")
        toolBar.addAction("Composition Analysis")


        toolBar.actionTriggered.connect(self.toolBarActionTriggered)
        self.addToolBar(Qt.TopToolBarArea, toolBar)


        #self.setCentralWidget(songList)

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



        
        

