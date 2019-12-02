import os
import pathlib
import threading
import time
from datetime import datetime
from functools import partial
from pathlib import Path

import numpy
import soundcard as sd
import wavio
from PySide2.QtCore import QCoreApplication, QSize, Qt, QThread, QTime, QUrl
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PySide2.QtWidgets import (QApplication, QCheckBox, QComboBox,
                               QDateTimeEdit, QDialog, QFileDialog,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QListWidget, QListWidgetItem,
                               QMessageBox, QPushButton, QSizePolicy, QSlider,
                               QSplitter, QStackedWidget, QStyle, QTextEdit,
                               QTimeEdit, QToolButton, QVBoxLayout, QWidget)

from custom import QDialogPlus
from SongList import SongList
from sqliteHandler import createTables, queries
from waveform import Waveform


class RecordIdeas(QWidget):
    def __init__(self, parent=None):
        super(RecordIdeas, self).__init__(parent)
        createTables()
        startTime = time.time()

        resourcesPath = os.getcwd()
        resourcesPath = os.path.join(resourcesPath, "resources")

        self.RECORD_ICON = QIcon(QPixmap(os.path.join(resourcesPath, "record.png")))
        self.PLAY_ICON = QIcon(QPixmap(os.path.join(resourcesPath, "play.png")))
        self.PAUSE_ICON = QIcon(QPixmap(os.path.join(resourcesPath, "pause.png")))
        self.STOP_ICON = QIcon(QPixmap(os.path.join(resourcesPath, "stop.png")))

        self.setupMediaPlayer()
        self.setupUi()

        print(time.time() - startTime)

    def setupMediaPlayer(self):
        self.mediaPlayer = QMediaPlayer()

        self.mediaPlayer.setNotifyInterval(1)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

    def setupUi(self):
        self.setWindowTitle("Recorded Ideas")
        mainLayout = QHBoxLayout(self)
        #splitterWidget.addWidget(widget)

        verticalListLayout = QVBoxLayout()

        self.recordedIdeasListWidget = QListWidget()
        self.recordedIdeasListWidget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        verticalListLayout.addWidget(self.recordedIdeasListWidget)

        miniHorizontalLayout = QHBoxLayout()
        locatorLine = QLineEdit()
        locatorLine.setPlaceholderText("Locator")
        locatorBox = QComboBox()
        items = ["Title", "Type", "Original Song", "Link",
        "Description", "All"]
        locatorBox.addItems(items)
        locatorBox.setCurrentIndex(len(items)-1)

        miniHorizontalLayout.addWidget(locatorLine)
        miniHorizontalLayout.addWidget(locatorBox)

        locatorLine.textChanged.connect(lambda:self.populateList(locatorLine.text(), locatorBox.currentText()))

        verticalListLayout.addLayout(miniHorizontalLayout)

        self.mainForm = QGroupBox()
        self.mainForm.setTitle("Details")

        mainLayout.addLayout(verticalListLayout)
        mainLayout.addWidget(self.mainForm)

        #
        #TODO

        #Size dialog -> half screen // use as self.VARIABLE at the start
        #screen/2
        #screen/2/3

        #mainForm setup

        self.populateList()
        self.mainFormSetupUi()
        #self.show()

        self.recordedIdeasListWidget.currentRowChanged.connect(self.changePage)

    def mainFormSetupUi(self):
        mainLayout = QVBoxLayout(self.mainForm)

        #Horizontal Layout 1
        horizontalLayout1 = QHBoxLayout()

        titleLabel = QLabel("Idea name:")
        self.titleEdit = QLineEdit()

        self.titleEdit.editingFinished.connect(partial(self.checkIdea, self.titleEdit))
        self.titleEdit.textChanged.connect(partial(self.validateIdea, self.titleEdit))

        horizontalLayout1.addWidget(titleLabel)
        horizontalLayout1.addWidget(self.titleEdit)

        #Horizontal Layout 2
        horizontalLayout2 = QHBoxLayout()
        typeLabel = QLabel("Type:")
        self.typeComboBox = QComboBox()

        self.typeComboBox.setEditable(True)

        dateLabel = QLabel("Date:")
        self.dateEdit = QDateTimeEdit()
        self.dateEdit.setCalendarPopup(True)

        horizontalLayout2.addWidget(typeLabel)
        horizontalLayout2.addWidget(self.typeComboBox)
        horizontalLayout2.addStretch(1)
        horizontalLayout2.addWidget(dateLabel)
        horizontalLayout2.addWidget(self.dateEdit)

        #Horizontal Layout 3
        horizontalLayout3 = QHBoxLayout()
        originalLabel = QLabel("Original song:")
        self.originalLine = QLineEdit()

        horizontalLayout3.addWidget(originalLabel)
        horizontalLayout3.addWidget(self.originalLine)

        #Horizontal Layout 4
        horizontalLayout4 = QHBoxLayout()

        linkLabel = QLabel("Link (optional):")
        self.linkLine = QLineEdit()

        horizontalLayout4.addWidget(linkLabel)
        horizontalLayout4.addWidget(self.linkLine)

        #Horizontal Layout 5
        horizontalLayout5 = QHBoxLayout()
        descriptionLabel = QLabel("Description:")

        minuteLabel = QLabel("Minute:")
        self.minuteLine = QTimeEdit()
        self.minuteLine.setDisplayFormat("mm:ss")

        horizontalLayout5.addWidget(descriptionLabel)
        horizontalLayout5.addWidget(minuteLabel)
        horizontalLayout5.addWidget(self.minuteLine)

        self.descriptionTextEdit = QTextEdit()

        #Horizontal Layout 6
        horizontalLayout6 = QHBoxLayout()
        locationLabel = QLabel("Location:")
        self.locationLine = QLineEdit()
        self.locationLine.setEnabled(False)
        self.locationButton = QPushButton("...")
        self.locationButton.clicked.connect(self.locateFile)

        horizontalLayout6.addWidget(locationLabel)
        horizontalLayout6.addWidget(self.locationLine)
        horizontalLayout6.addWidget(self.locationButton)

        #Recording laboratory, set visibles in function
        self.recordGroupBox = QGroupBox()
        self.recordGroupBox.setTitle("Recording Laboratory")

        verticalMainGroupLayout = QVBoxLayout(self.recordGroupBox)
        horizontalRecordLayout1 = QHBoxLayout()

        self.waveFormLabel = QLabel("Waveform not ready yet")

        self.recordButton = QPushButton()
        self.recordButton.setIcon(self.RECORD_ICON)
        self.recordButton.setMinimumSize(50,50)
        self.recordButton.setIconSize(QSize(50, 50))
        self.recordButton.clicked.connect(self.record)
        self.recordButton.setCursor(Qt.PointingHandCursor)
        horizontalRecordLayout1.addWidget(self.waveFormLabel)
        horizontalRecordLayout1.addStretch(1)
        horizontalRecordLayout1.addWidget(self.recordButton)

        horizontalRecordLayout2 = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderReleased.connect(self.playSlider)
        self.slider.setStyleSheet("QSlider::handle:horizontal { border: 1px solid #777; background:#b55858;}");
        horizontalRecordLayout2.addWidget(self.slider)

        horizontalRecordLayout3 = QHBoxLayout()
        self.playButton = QPushButton()
        self.stopButton = QPushButton()

        self.playButton.setIcon(self.PLAY_ICON)
        self.stopButton.setIcon(self.STOP_ICON)

        self.playButton.clicked.connect(self.playSong)
        self.stopButton.clicked.connect(self.stopSong)

        horizontalRecordLayout3.addStretch(1)
        horizontalRecordLayout3.addWidget(self.playButton)
        horizontalRecordLayout3.addWidget(self.stopButton)
        horizontalRecordLayout3.addStretch(1)

        verticalMainGroupLayout.addLayout(horizontalRecordLayout1)
        verticalMainGroupLayout.addLayout(horizontalRecordLayout2)
        verticalMainGroupLayout.addLayout(horizontalRecordLayout3)

        #Horizontal Layout 7
        horizontalLayout7 = QHBoxLayout()
        self.saveButton = QPushButton()
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveRecording)

        horizontalLayout7.addStretch(1)
        horizontalLayout7.addWidget(self.saveButton)

        #Adding Layouts to main
        mainLayout.addLayout(horizontalLayout1)
        mainLayout.addLayout(horizontalLayout2)
        mainLayout.addLayout(horizontalLayout3)
        mainLayout.addLayout(horizontalLayout4)
        mainLayout.addLayout(horizontalLayout5)
        mainLayout.addWidget(self.descriptionTextEdit)
        mainLayout.addLayout(horizontalLayout6)
        mainLayout.addWidget(self.recordGroupBox)
        mainLayout.addLayout(horizontalLayout7)

    def clearForm(self):
        self.titleEdit.clear()
        self.typeComboBox.clear()
        self.originalLine.clear()
        self.dateEdit.clear()
        self.linkLine.clear()
        self.minuteLine.clear()
        self.descriptionTextEdit.clear()
        self.locationLine.clear()
        self.waveFormLabel.setText("Waveform not ready yet")

    def populateForm(self, title): #title is the primary key
        listArray = queries("""SELECT title, type, original_song, link, description,
        location, minute, timestamp from recorded_ideas where title = ?""", (title,))
        print(listArray)
        if len(listArray) != 0:
            title = listArray[0][0]
            _type = listArray[0][1]
            original_song = listArray[0][2]
            link = listArray[0][3]
            description = listArray[0][4]
            location = listArray[0][5]
            minute = listArray[0][6]
            timestamp = listArray[0][7]
        else:
            title = None
            _type = None
            original_song = None
            link = None
            description = None
            location = None
            minute = None
            timestamp = None

        typeArray = ["Select..."] #Combo Box stuff
        for typeSingle in queries("SELECT type from recorded_ideas"):
            if typeSingle[0] not in typeArray:
                typeArray.append(typeSingle[0])

        if title != None: self.titleEdit.setText(title)
        self.typeComboBox.addItems(typeArray)
        if _type != None: self.typeComboBox.setCurrentText(_type)
        if timestamp != None: self.dateEdit.setDateTime(datetime.strptime(timestamp, '%d/%m/%Y %H:%M'))
        else: self.dateEdit.setDateTime(datetime.now())#default

        if original_song != None: self.originalLine.setText(original_song)
        if link != None: self.linkLine.setText(link)
        if minute != None:
            time = QTime(0,0,0)
            self.minuteLine.setTime(time.addSecs(minute))
        if description != None: self.descriptionTextEdit.setText(description)
        if location != None:
            self.locationLine.setText(location)
            self.locationButton.setEnabled(False)

        self.waveFormAvailable()

    def populateList(self, locatorItem=None, locatorColumn=None):
        print(locatorItem, locatorColumn)
        self.recordedIdeasListWidget.blockSignals(True)
        self.recordedIdeasListWidget.clear()
        if locatorItem == None or locatorItem == "":
            listArray = queries("""SELECT title, type, original_song, link, description,
            location, minute, timestamp from recorded_ideas """)
        else:
            if locatorColumn != "All": #No strings concatenation, no security holes
                if locatorColumn == "Title":
                    sql = """SELECT title, type, original_song, link, description,
                    location, minute, timestamp from recorded_ideas where title LIKE ?"""
                elif locatorColumn == "Type":
                    sql = """SELECT title, type, original_song, link, description,
                    location, minute, timestamp from recorded_ideas where type LIKE ?"""
                elif locatorColumn == "Original Song":
                    sql = """SELECT title, type, original_song, link, description,
                    location, minute, timestamp from original_song where title LIKE ?"""
                elif locatorColumn == "Link":
                    sql = """SELECT title, type, original_song, link, description,
                    location, minute, timestamp from original_song where link LIKE ?"""
                elif locatorColumn == "Description":
                    sql = """SELECT title, type, original_song, link, description,
                    location, minute, timestamp from original_song where description LIKE ?"""

                locatorItem = "%" + locatorItem + "%"
                listArray = queries(sql, (locatorItem,))
            else:
                locatorItem = "%" + locatorItem + "%"
                variables = [locatorItem, locatorItem, locatorItem, locatorItem, locatorItem]
                listArray = queries("""SELECT title, type, original_song, link, description,
                location, minute, timestamp from recorded_ideas where title LIKE ? OR type LIKE ?
                OR original_song LIKE ? OR link LIKE ? OR description LIKE ?""", variables)
        for item in listArray:
            title = item[0]
            _type = item[1]
            timestamp = item[7]
            try:
                timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
                timestamp = timestamp.strftime("%d/%m/%Y")
            except:
                timestamp = ""

            text = "%s %s %s" % (title, _type, timestamp)
            qItem = QListWidgetItem(text)
            qItem.setData(Qt.UserRole, title)
            self.recordedIdeasListWidget.addItem(qItem)
        #new idea
        qItem = QListWidgetItem("New song...")
        qItem.setData(Qt.UserRole, "New song...") #otherwise that would be an error
        self.recordedIdeasListWidget.addItem(qItem)
        self.recordedIdeasListWidget.blockSignals(False)
    def changePage(self, index):
        title = self.recordedIdeasListWidget.item(index).data(Qt.UserRole)
        self.clearForm()
        self.populateForm(title)
        self.slider.setValue(0)

    def checkIdea(self):
        text = self.titleEdit.text()
        sql = "SELECT title from recorded_ideas where title = ?"
        if len(queries(sql, (text,))) != 0:
            self.titleEdit.setText("")
    def validateIdea(self, widget):
        """if self.listStackedWidget.currentIndex() != self.listStackedWidget.count() - 1:
            msg = QMessageBox.question(self, 'Change title?', 'Do you want to change the title?', QMessageBox.Yes, QMessageBox.No)
            if msg == QMessageBox.Yes:
                pass#TODO change file path, widgets and press save
        else:
                widget.blockSignals(True)
                widget.undo()
                widget.blockSignals(False)"""
        pass
    #TODO PROMPT NEW TITLE
    def record(self):
        print("recording")
        songName = self.titleEdit.text()

        if len(songName) > 0 and len(self.locationLine.text()) == 0:
            self.recordDialog = QDialogPlus()
            self.recordDialog.setWindowTitle("Recording...")
            self.recordDialog.setModal(True)
            self.recordDialog.setWindowIcon(self.RECORD_ICON)

            layout = QHBoxLayout(self.recordDialog)

            label = QLabel("<b>Recording...</b><br><br>press Space to stop.")
            layout.addWidget(label)

            self.recordingEnabled = True

            self.recordDialog.signalSpacePressed.connect(self.stopRecording)

            self.recordThread = QThread()
            self.recordThread.started.connect(self.startRecording)
            self.recordThread.start()

            self.recordDialog.show()

    def startRecording(self):
        recordFolder = os.getcwd()
        recordFolder = os.path.join(recordFolder, "recordings")

        if not os.path.isdir(recordFolder):
            os.mkdir(recordFolder)

        speaker = sd.default_speaker()
        speakerLoopback = sd.get_microphone(speaker._id, include_loopback=True)
        arrays = []

        data = None
        while self.recordingEnabled:
            with speakerLoopback.recorder(samplerate=44100, channels=2) as mic:
                for _ in range(1000000):
                    if self.recordingEnabled:
                        QCoreApplication.processEvents()
                        data = mic.record(numframes=1024)#, samplerate=44100, channels=2)
                        arrays.append(data)
                    else:
                        break

            self.waveFormLabel.setText("Creating Waveform...")
            QCoreApplication.processEvents()
            dummyArray = numpy.array([[0, 0]])
            for array in arrays:
                dummyArray = numpy.concatenate((dummyArray, array))

            data = numpy.array(dummyArray)

            songName = self.titleEdit.text()
            fileName = os.path.join(recordFolder, songName + ".wav")
            if self.locationLine != None: self.locationLine.setText(fileName)

            wavio.write(fileName, data, 44100, sampwidth=2)

            self.waveFormPicture = Waveform(fileName).save()
            self.waveFormAvailable()

        return True
    def waveFormAvailable(self):
        #TODO access both ways

        available = True

        self.recordedFile = os.getcwd()
        self.recordedFile = os.path.join(self.recordedFile, "recordings")
        self.recordedFile = os.path.join(self.recordedFile, self.titleEdit.text()) #TODO CHANGE TO LOCATION
        self.recordedFile = self.recordedFile + '.wav'
        #self.recordedFile = self.locationLine.text()
        if os.path.exists(self.recordedFile):
            file = wavio.read(self.recordedFile)
            wafeFormPixmap = QPixmap(Waveform(self.recordedFile).save())
        else:
            available = False
        if available:
            self.waveFormLabel.setPixmap(wafeFormPixmap)

        self.recordButton.setVisible(not available)

        self.playlist = QMediaPlaylist()
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(self.recordedFile)))
        self.mediaPlayer.setPlaylist(self.playlist)

        self.slider.setVisible(available)
        self.playButton.setVisible(available)
        self.stopButton.setVisible(available)

    def playSong(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.PAUSE_ICON)
        else:
            self.playButton.setIcon(self.PLAY_ICON)
    def positionChanged(self, position):
        if position != self.mediaPlayer.duration():
            self.slider.setValue(position)
    def durationChanged(self, duration):
        if duration != self.mediaPlayer.position():
            self.slider.setRange(0, duration)
    def playSlider(self):
        self.mediaPlayer.setPosition(self.slider.value())

    def stopSong(self):
        self.mediaPlayer.stop()

    def locateFile(self):
        self.fileSystem = QFileDialog()
        self.fileSystem.show()
        self.fileSystem.fileSelected.connect(self.fileLoaded)

    def fileLoaded(self, path):
        self.locationLine.setText(path)
        try:
            self.playlist = QMediaPlaylist()
            self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(path)))
            self.mediaPlayer.setPlaylist(self.playlist)
        except:
            print("fail")
        self.slider.setVisible(True)
        self.playButton.setVisible(True)
        self.stopButton.setVisible(True)

    def stopRecording(self):
        self.recordingEnabled = False
        self.recordThread.terminate()
        self.recordDialog.hide()

    def saveRecording(self):
        title = self.titleEdit.text()
        _type = self.typeComboBox.currentText()
        original_song = self.originalLine.text()
        date = self.dateEdit.text()
        minute = self.minuteLine.time()
        minute = QTime(0, 0).secsTo(minute)
        link = self.linkLine.text()
        description = self.descriptionTextEdit.toPlainText()
        location = self.locationLine.text()

        variables = [title, _type, date, original_song, \
        minute, link, description, location]

        print(variables)
        sql = """INSERT OR REPLACE into recorded_ideas
        (title, type, timestamp, original_song, minute,
        link, description, location)
                values
        (?,      ?,       ?,         ?,      ?,
         ?,      ?,         ?)

        """
        #TODO If exists, do you want to replace, etc?

        queries(sql, variables)
        self.populateList()


if __name__ == '__main__':
    app = QApplication([])
    recordIdeas = RecordIdeas()
    #recordIdeas.show()
    app.exec()
