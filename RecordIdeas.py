from PyQt5.QtWidgets import QApplication, QDialog, QListWidget, QListWidgetItem, QDialog, QApplication,\
     QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QMessageBox, QStackedWidget, QLineEdit,\
     QWidget, QComboBox, QGridLayout, QCheckBox, QGroupBox, QTextEdit, QPushButton, QTimeEdit,\
     QDateTimeEdit, QToolButton, QSlider
from PyQt5.QtCore import Qt, QTime, QSize, QThread, QCoreApplication, QUrl
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent

from custom import QDialogPlus
from sqliteHandler import createTables, queries
import soundcard as sd
import numpy
import pyaudio
import wavio
import time
import threading
import keyboard
from functools import partial
from datetime import datetime
import os
from pathlib import Path
from waveform import Waveform
import pathlib

global enable
enable = True

from SongList import SongList

class RecordIdeas(QDialog):
    def __init__(self, parent=None):
        super(RecordIdeas, self).__init__(parent)
        createTables()
        self.dateNow = datetime.now()
        self.RECORD_ICON = QIcon(QPixmap(r"I:\RaulCoding\resources\record.png"))
        self.PLAY_ICON = QIcon(QPixmap(r"I:\RaulCoding\resources\play.png"))
        self.STOP_ICON = QIcon(QPixmap(r"I:\RaulCoding\resources\stop.png"))
        
        self.player = QMediaPlayer()

        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Recorded Ideas")
        self.mainLayout = QHBoxLayout(self)  
        self.recordedIdeasListWidget = QListWidget()
        self.listStackedWidget = QStackedWidget()

        
        self.mainLayout.addWidget(self.recordedIdeasListWidget)
        self.mainLayout.addWidget(self.listStackedWidget)

        self.show()

        self.thread = QThread()
        self.thread.started.connect(self.setupListWidget)
        self.thread.start()

        self.recordedIdeasListWidget.currentRowChanged.connect(self.changePage)
    def setupListWidget(self):
        self.recordedIdeasListWidget.clear()
        listArray = queries("""SELECT title, type, original_song, link, description,
        location, minute, timestamp from recorded_ideas order by timestamp""")
        for item in listArray:
            title = item[0]
            _type = item[1]
            timestamp = item[7]
            try:
                timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
                timestamp = timestamp.strftime("%d/%m/%Y")
            except:
                timestamp = "no"

            text = "%s %s %s" % (title, _type, timestamp)
            qItem = QListWidgetItem(text)
            self.recordedIdeasListWidget.addItem(qItem)
            #print(title, _type, timestamp)
        dummy = []
        for item in listArray: dummy.append(item[0])
        #print("--------------------------------$$$$$$$$$$$$$", dummy)
        #self.stackedWidget(listArray)
        self.stackedWidget([])

    def stackedWidget(self, listArray):
        x = 0

        while x < self.listStackedWidget.count():
            widget = self.listStackedWidget.widget(x)
            self.listStackedWidget.removeWidget(widget)
            widget.deleteLater()

        typeArray = ["Select..."]
        for typeSingle in queries("SELECT type from recorded_ideas"):
            if typeSingle[0] not in typeArray:
                typeArray.append(typeSingle[0])

        arrayNew = [None, None, None, None, None, None, None, None] #only need one for validation
        listArray.append(arrayNew)
        qItem = QListWidgetItem("Add new song...")
        self.waveFormPicture = None
        self.recordedIdeasListWidget.addItem(qItem)
        for item in listArray:
            #items
            title = item[0]
            _type = item[1]
            original_song = item[2]
            link = item[3]
            description = item[4]
            location = item[5]
            minute = item[6]
            timestamp = item[7]
            
            #UI SETUP
            widgetPage = QWidget()
            mainLayout = QVBoxLayout(widgetPage)
            
            horizontalLayout1 = QHBoxLayout()
            titleLabel = QLabel("Idea name:")
            self.titleEdit = QLineEdit()
            if title != None: 
                self.titleEdit.setText(title)

            self.titleEdit.setAccessibleName("Title")
            self.titleEdit.editingFinished.connect(partial(self.checkIdea, self.titleEdit))
            self.titleEdit.textChanged.connect(partial(self.validateIdea, self.titleEdit))

            horizontalLayout1.addWidget(titleLabel)
            horizontalLayout1.addWidget(self.titleEdit)

            #in a function to retrieve existing


            horizontalLayout2 = QHBoxLayout()
            typeLabel = QLabel("Type:")
            typeComboBox = QComboBox()
            typeComboBox.addItems(typeArray)

            if _type != None: typeComboBox.setCurrentText(_type)
            typeComboBox.setAccessibleName("Type")
            typeComboBox.setEditable(True)

            dateLabel = QLabel("Date:")
            dateEdit = QDateTimeEdit()
            dateEdit.setCalendarPopup(True)
            dateEdit.setAccessibleName("Date")
            if timestamp != None: dateEdit.setDateTime(datetime.strptime(timestamp, '%d/%m/%Y %H:%M'))
            else: dateEdit.setDateTime(datetime.now())#default

            horizontalLayout2.addWidget(typeLabel)
            horizontalLayout2.addWidget(typeComboBox)
            horizontalLayout2.addStretch(1)
            horizontalLayout2.addWidget(dateLabel)
            horizontalLayout2.addWidget(dateEdit)

            horizontalLayout3 = QHBoxLayout()
            originalLabel = QLabel("Original song:")
            originalLine = QLineEdit()
            
            if original_song != None: originalLine.setText(original_song)
            originalLine.setAccessibleName("Original Song")

            horizontalLayout3.addWidget(originalLabel)
            horizontalLayout3.addWidget(originalLine)

            horizontalLayout4 = QHBoxLayout()

            linkLabel = QLabel("Link (optional):")
            linkLine = QLineEdit()

            if link != None: linkLine.setText(link)
            linkLine.setAccessibleName("Link")

            horizontalLayout4.addWidget(linkLabel)
            horizontalLayout4.addWidget(linkLine)

            horizontalLayout5 = QHBoxLayout()
            descriptionLabel = QLabel("Description:")

            minuteLabel = QLabel("Minute:")
            self.minuteLine = QTimeEdit()
            self.minuteLine.setDisplayFormat("mm:ss")
            self.minuteLine.setAccessibleName("Minute")
            if minute != None:
                time = QTime(0,0,0)
                self.minuteLine.setTime(time.addSecs(minute))
            
            horizontalLayout5.addWidget(descriptionLabel)
            horizontalLayout5.addWidget(minuteLabel)
            horizontalLayout5.addWidget(self.minuteLine)

            descriptionTextEdit = QTextEdit()
            if description != None: descriptionTextEdit.setText(description)
            descriptionTextEdit.setAccessibleName("Description")

            horizontalLayout6 = QHBoxLayout()
            locationLabel = QLabel("Location:")
            locationLine = QLineEdit()
            locationLine.setAccessibleName("Location")
            locationLine.setEnabled(False)
            locationButton = QPushButton("...")
            if location != None: 
                locationLine.setText(location)
                locationButton.setEnabled(False)

            horizontalLayout6.addWidget(locationLabel)
            horizontalLayout6.addWidget(locationLine)
            horizontalLayout6.addWidget(locationButton)

            #Recording laboratory, set visibles in function
            self.recordGroupBox = QGroupBox()
            self.recordGroupBox.setTitle("Recording Laboratory")

            verticalMainGroupLayout = QVBoxLayout(self.recordGroupBox)
            horizontalRecordLayout1 = QHBoxLayout()

            self.waveFormLabel = QLabel("Waveform not ready yet")
            #TODO Create waveform on the go with temp

            self.recordButton = QPushButton()
            self.recordButton.setIcon(self.RECORD_ICON)
            self.recordButton.setMinimumSize(50,50)
            self.recordButton.setIconSize(QSize(50, 50))
            self.recordButton.clicked.connect(partial(self.record, self.titleEdit, locationLine))
            self.recordButton.setCursor(Qt.PointingHandCursor)
            horizontalRecordLayout1.addWidget(self.waveFormLabel)
            horizontalRecordLayout1.addStretch(1)
            horizontalRecordLayout1.addWidget(self.recordButton)

            horizontalRecordLayou2 = QHBoxLayout()
            slider = QSlider()

            horizontalRecordLayout3 = QHBoxLayout()
            self.playButton = QPushButton()
            self.stopButton = QPushButton()

            self.playButton.setIcon(self.PLAY_ICON)
            self.stopButton.setIcon(self.STOP_ICON)

            self.playButton.clicked.connect(partial(self.playSong, locationLine))
            self.stopButton.clicked.connect(self.stopSong)
            
            horizontalRecordLayout3.addStretch(1)
            horizontalRecordLayout3.addWidget(self.playButton)
            horizontalRecordLayout3.addWidget(self.stopButton)
            horizontalRecordLayout3.addStretch(1)

            verticalMainGroupLayout.addLayout(horizontalRecordLayout1)
            verticalMainGroupLayout.addLayout(horizontalRecordLayout3)

            self.waveFormAvailable()
            
            horizontalLayout7 = QHBoxLayout()
            saveButton = QPushButton()
            saveButton.setText("Save")
            saveButton.clicked.connect(partial(self.saveRecording, widgetPage))
            
            horizontalLayout7.addStretch(1)
            horizontalLayout7.addWidget(saveButton)

            mainLayout.addLayout(horizontalLayout1)
            mainLayout.addLayout(horizontalLayout2)
            mainLayout.addLayout(horizontalLayout3)
            mainLayout.addLayout(horizontalLayout4)
            mainLayout.addLayout(horizontalLayout5)
            mainLayout.addWidget(descriptionTextEdit)
            mainLayout.addLayout(horizontalLayout6)
            mainLayout.addWidget(self.recordGroupBox)
            mainLayout.addLayout(horizontalLayout7)

            x=+1

            self.listStackedWidget.addWidget(widgetPage)
        dateTime = datetime.now()
        print(dateTime, "<----")
        print(dateTime - self.dateNow)
        return self.listStackedWidget
        
    def changePage(self, index):
        self.listStackedWidget.setCurrentIndex(index)
        self.recordedIdeasListWidget.setCurrentRow(index)
    
    def checkIdea(self, widget):
        currentIndexStacked = widget.parentWidget().parentWidget().currentIndex()
        
        if self.listStackedWidget.currentIndex() == self.listStackedWidget.count() - 1:
            text = widget.text()
            sql = "SELECT title from recorded_ideas where title = ?"
            if len(queries(sql, (text,))) != 0:
                widget.setText("")
    def validateIdea(self, widget):
        #print("--£££££££££££££££", self.listStackedWidget.currentIndex())
        if self.listStackedWidget.currentIndex() != self.listStackedWidget.count() - 1:
            msg = QMessageBox.question(self, 'Change title?', 'Do you want to change the title?', QMessageBox.Yes, QMessageBox.No)
            if msg == QMessageBox.Yes:
                pass#TODO change file path, widgets and press save
            else:
                widget.blockSignals(True)
                widget.undo()
                widget.blockSignals(False)

    def record(self, songTitleWidget, locationLineWidget):
        #print("recording1")
        songName = songTitleWidget.text()

        if len(songName) > 0 and len(locationLineWidget.text()) == 0:
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
            self.recordThread.started.connect(partial(self.startRecording, songName, locationLineWidget))
            self.recordThread.start()

            self.recordDialog.show()

            #self.recordThread.create(self.startRecording, songName, locationLineWidget)
            
            #self.recordDialog.connect(self.recordThread, lambda: self.startRecording(songName, locationLineWidget))

            #self.recordThread.started.connect(lambda: self.startRecording(songName, locationLineWidget))
            #threading.Thread(target=self.startRecording(songName, locationLineWidget))
            #self.recordThread.start()

    def startRecording(self, songName="", locationLineWidget=None):
        #print("start Recording")
        x = 0

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
                        #print("recording", _)
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
            
            fileName = os.path.join(recordFolder, songName + ".wav")
            if locationLineWidget != None: locationLineWidget.setText(fileName)

            wavio.write(fileName, data, 44100, sampwidth=2)

            self.waveFormPicture = Waveform(fileName).save()
            self.waveFormAvailable()

        return True
    def waveFormAvailable(self):
        #TODO access both ways
        #print("in wave form")

        available = True

        self.recordedFile = os.getcwd()
        self.recordedFile = os.path.join(self.recordedFile, "recordings")
        self.recordedFile = os.path.join(self.recordedFile, self.titleEdit.text())
        self.recordedFile = self.recordedFile + '.wav'
        if os.path.exists(self.recordedFile):
            file = wavio.read(self.recordedFile)
            wafeFormPixmap = QPixmap(Waveform(self.recordedFile).save())
        else:
            available = False
        if available: 
            self.waveFormLabel.setPixmap(wafeFormPixmap)
        
        self.recordButton.setVisible(not available)
        
        self.playButton.setVisible(available)
        self.stopButton.setVisible(available)

    def playSong(self, locationLine):
        self.recordedFile = locationLine.text()
        #print(locationLine)
        #print("riviera paradise", self.recordedFile)
        #self.recordedFile = pass
        self.playlist = QMediaPlaylist()
        self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(self.recordedFile)))
        self.player.setPlaylist(self.playlist)
        self.player.play()

    def stopSong(self):
        self.player.stop()

    def stopRecording(self):
        #print("in stop recording")
        self.recordingEnabled = False
        self.recordThread.terminate()
        self.recordDialog.hide()
        
    def saveRecording(self, widgetPage):
        title = ""
        _type = ""
        date = ""
        original_song = ""
        minute = ""
        link = ""
        description = ""
        location = ""

        for widget in widgetPage.children():
            #print(widget)
            if not isinstance(widget, (QHBoxLayout, QVBoxLayout)):
                if widget.accessibleName() == "Title": title = widget.text()
                elif widget.accessibleName() == "Type":  _type = widget.currentText() #Combo Box
                elif widget.accessibleName() == "Date":  date = widget.text()#Date 
                elif widget.accessibleName() == "Original Song": original_song = widget.text()
                elif widget.accessibleName() == "Minute": 
                    time = widget.time()
                    minute = QTime(0, 0).secsTo(time)
                elif widget.accessibleName() == "Link": link = widget.text()#QComboBox 
                elif widget.accessibleName() == "Description":  description = widget.toPlainText()#QTextEdit
                elif widget.accessibleName() == "Location":  location = widget.text()#QLineEdit

        variables = [title, _type, date, original_song, \
        minute, link, description, location]

        #print("---------", variables)

        sql = """INSERT OR REPLACE into recorded_ideas 
        (title, type, timestamp, original_song, minute,
        link, description, location)
                values 
        (?,      ?,       ?,         ?,      ?,
         ?,      ?,         ?)


        """
        #ON CONFLICT(id) do update set title=EXCLUDED.title, type=EXCLUDED.type, 
        #timestamp=EXCLUDED.timestamp, original_song=EXCLUDED.original_song, 
        #minute=EXCLUDED.minute, link=EXCLUDED.link, 
        #description=EXCLUDED.description, location=EXCLUDED.location"""

        queries(sql, variables)
        
        self.thread2 = QThread()
        self.thread2.started.connect(self.setupListWidget)
        self.thread2.start()

        date = datetime.strptime(date, "%d/%m/%Y %H:%M")
        date = date.strftime("%d/%m/%Y")
        text = "%s %s %s" % (title, _type, date)
        print(text)
        x = 0
        while x < self.recordedIdeasListWidget.count():
            qItem = self.recordedIdeasListWidget.item(x)
            if qItem.text() == text:
                index = x
                break
            x +=1
        
        #self.changePage(index)
        #self.listStackedWidget.repaint()
        #self.recordedIdeasListWidget.setCurrentRow()

        
        #TODO CAREFUL WITH THE LISTS

if __name__ == '__main__':
    app = QApplication([])
    recordIdeas = RecordIdeas()
    #recordIdeas.show()
    app.exec()




        

