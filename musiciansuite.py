from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QMessageBox, QAction,\
                            QShortcut
from PyQt5.QtGui import QPixmap, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QSharedMemory, QIODevice, QEvent, pyqtSignal

from PyQt5.QtNetwork import QLocalServer, QLocalSocket

#Originally designed for PySide2, so had to do hybrid here
#Might port everything back to PyQt5 for ease

import sys
import os

from mainwindow import MusicMainWindow
from sqliteHandler import createTables

class MusicianSuite(QApplication): 
    signalReceived = pyqtSignal(object)
    messageReceived = pyqtSignal()
    def __init__(self, argv, key):
        super().__init__(argv)
        QSharedMemory(key).attach()
        self._memory = QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())
        self._key = key
        self._timeout = 1000
        self._server = QLocalServer(self)
        if not self.isRunning():
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    
    def isRunning(self):
        return self._running

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.signalReceived.emit(
                socket.readAll().data().decode('utf-8'))
            socket.disconnectFromServer()
        else:
            Qt.QDebug(socket.errorString())

    def sendNotification(self, message):
        if self.isRunning():
            socket = QLocalSocket(self)
            socket.connectToServer(self._key, QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                print(socket.errorString())
                return False
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            socket.write(message)
            if not socket.waitForBytesWritten(self._timeout):
                print(socket.errorString())
                return False
            socket.disconnectFromServer()
            return True
        return False

    def init(self):
        """True initiation of the App, if only one instance"""
        createTables()
        self.mainWindow = MusicMainWindow()
        resourcesPath = os.getcwd()
        resourcesPath = os.path.join(resourcesPath, "resources")
        if not os.path.exists(resourcesPath):
            os.mkdir(resourcesPath)

        self.MAIN_ICON = QIcon(os.path.join(resourcesPath, "test.ico"))
        self.ICON0 = QIcon(QPixmap(os.path.join(resourcesPath, "icon0.png")))
        self.ICON1 = QIcon(QPixmap(os.path.join(resourcesPath, "icon1.png")))
        self.RECORD_ICON = QIcon(QPixmap(os.path.join(resourcesPath, "record.png")))

        self.widget = QWidget()
        self.trayIcon = QSystemTrayIcon(self.MAIN_ICON, self.widget)
        self.trayIcon.setToolTip("Musician Suite")
        self.trayIconMenu = QMenu()

        self.songListAction = QAction(self.ICON0, "Song List")
        self.recordIdeasAction = QAction(self.ICON1, "Recorded Ideas")
        self.recordAction = QAction(self.RECORD_ICON, "Record now!")
        self.exitAction = QAction("Exit")

        self.trayIconMenu.addAction(self.songListAction)
        self.trayIconMenu.addAction(self.recordIdeasAction)
        self.trayIconMenu.addAction(self.recordAction)
        self.trayIconMenu.addAction(self.exitAction)

        self.trayIcon.setContextMenu(self.trayIconMenu)
        
        self.trayIcon.show()

        self.trayIcon.activated.connect(self.iconDoubleClickMain)
        self.trayIconMenu.triggered.connect(self.messagePopup)
        
        self.mainWindow.stackedWidget.setCurrentIndex(0)

        self.mainWindow.show()
    def iconDoubleClickMain(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:  
            self.startRecordingHook()
    def messagePopup(self, action):
        """Pressing the menu and toast """
        if action == self.songListAction:
            if not self.mainWindow.isVisible(): 
                self.mainWindow.stackedWidget.setCurrentIndex(0)
                self.mainWindow.show()
        elif action == self.recordIdeasAction:
            if not self.mainWindow.isVisible(): 
                self.mainWindow.stackedWidget.setCurrentIndex(1)
                self.mainWindow.show()
        elif action == self.recordAction:
            self.startRecordingHook()
        else:
            self.exit()

    def startRecordingHook(self):
        self.mainWindow.stackedWidget.setCurrentIndex(1)
        self.mainWindow.show()
        listRows = self.mainWindow.recordIdeas.recordedIdeasListWidget.count()
        print(listRows)
        self.mainWindow.recordIdeas.recordedIdeasListWidget.setCurrentRow(listRows-1)
        self.mainWindow.recordIdeas.record()
if __name__ == '__main__':
    app = MusicianSuite(sys.argv, 'Musician Suite')
    if app.isRunning():
        msg = 'App Running'
        app.sendNotification(msg)  
        print('app is already running')
        sys.exit(1)
    else:
        #try:
            app.init()
        #except Exception as e:
            #msgBox = QMessageBox()
            #msgBox.setText("Musician Suite has encountered an error and needs to close.\n\nTry again.")
            #msgBox.exec_()
    sys.exit(app.exec_())
