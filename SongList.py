from PyQt5.QtWidgets import QDialog, QListWidget, QListWidgetItem, QDialog, QApplication,\
     QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QMessageBox, QStackedWidget, QLineEdit,\
     QWidget, QComboBox, QGridLayout, QCheckBox, QGroupBox, QTextEdit, QPushButton, QTimeEdit,\
     QDateTimeEdit, QCompleter, QSlider, QFileDialog
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import QTime, Qt, QDir, QUrl
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from datetime import datetime, timedelta
from sqliteHandler import queries
import numpy as np
import os
from functools import partial

class SongList(QWidget):
    def __init__(self, parent=None):
        super(SongList, self).__init__(parent)

        resourcesPath = os.getcwd()
        resourcesPath = os.path.join(resourcesPath, "resources")

        self.PLAY_ICON = QIcon(QPixmap(os.path.join(resourcesPath, "play.png")))
        self.PAUSE_ICON = QIcon(QPixmap(os.path.join(resourcesPath, "pause.png")))
        self.STOP_ICON = QIcon(QPixmap(os.path.join(resourcesPath, "stop.png")))

        self.setupMediaPlayer()
        self.setupUi()
    
    def setupMediaPlayer(self):
        self.mediaPlayer = QMediaPlayer()

        self.mediaPlayer.setNotifyInterval(1)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

    def setupUi(self):
        self.setWindowTitle("List of songs")
        mainLayout = QHBoxLayout(self)

        verticalListLayout = QVBoxLayout()
        self.songsListWidget = QListWidget()
        verticalListLayout.addWidget(self.songsListWidget)

        miniHorizontalLayout = QHBoxLayout()
        locatorLine = QLineEdit()
        locatorLine.setPlaceholderText("Locator")
        locatorBox = QComboBox()
        items = ["Title", "Status", "Description", "Style", "All"]
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

        self.populateList()
        self.mainFormSetupUi()
        #self.show()

        self.songsListWidget.currentRowChanged.connect(self.changePage)

    def mainFormSetupUi(self):
        
        """title, status style, duration, descriptin, location, project,
        variation_another_song, timestamp"""

        mainLayout = QVBoxLayout(self.mainForm)

        #Horizontal Layout 1
        horizontalLayout1 = QHBoxLayout()

        titleLabel = QLabel("Song name:")
        self.titleEdit = QLineEdit()

        #self.titleEdit.editingFinished.connect(partial(self.checkIdea, self.titleEdit))
        #self.titleEdit.textChanged.connect(partial(self.validateIdea, self.titleEdit))

        horizontalLayout1.addWidget(titleLabel)
        horizontalLayout1.addWidget(self.titleEdit)

        
        #Horizontal Layout 2
        horizontalLayout2 = QHBoxLayout()
        statusLabel = QLabel("Status:")
        self.statusBox = QComboBox()
        
        dateLabel = QLabel("Date:")
        self.dateEdit = QDateTimeEdit()
        self.dateEdit.setCalendarPopup(True)

        horizontalLayout2.addWidget(statusLabel)
        horizontalLayout2.addWidget(self.statusBox)
        horizontalLayout2.addStretch(1)
        horizontalLayout2.addWidget(dateLabel)
        horizontalLayout2.addWidget(self.dateEdit)


        #Style Groupbox, widgets added automatically
        self.styleGroupBox = QGroupBox()
        self.styleGroupBox.setTitle("Style:")
        self.styleLayout = QGridLayout(self.styleGroupBox)
        
        horizontalLayout3 = QHBoxLayout()
        durationLabel = QLabel("Duration:")
        self.durationLine = QTimeEdit()
        self.durationLine.setDisplayFormat("mm:ss")
        
        projectLabel = QLabel("Project")

        self.projectComboBox = QComboBox()
        self.projectComboBox.setEditable(True)
        
        horizontalLayout3.addWidget(durationLabel)    
        horizontalLayout3.addWidget(self.durationLine)
        horizontalLayout3.addWidget(projectLabel)
        horizontalLayout3.addWidget(self.projectComboBox)

        horizontalLayout4 = QHBoxLayout()
        descriptionLabel = QLabel("Description:")
        variationLabel = QLabel("Variation from another song: ")
        self.variationLine = QLineEdit()
        
        horizontalLayout4.addWidget(descriptionLabel)
        horizontalLayout4.addStretch(1)
        horizontalLayout4.addWidget(variationLabel)
        horizontalLayout4.addWidget(self.variationLine)

        self.descriptionTextEdit = QTextEdit()

        horizontalLayout5 = QHBoxLayout()
        locationLabel = QLabel("Location:")
        self.locationLine = QLineEdit()
        self.locationButton = QPushButton("...")
        self.locationButton.clicked.connect(self.locateFile)

        
        horizontalLayout5.addWidget(locationLabel)
        horizontalLayout5.addWidget(self.locationLine)
        horizontalLayout5.addWidget(self.locationButton)

        horizontalLayout6 = QHBoxLayout()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.sliderReleased.connect(self.playSlider)
        self.slider.setStyleSheet("QSlider::handle:horizontal { border: 1px solid #777; background:#b55858;}")
        horizontalLayout6.addWidget(self.slider)

        horizontalLayout7 = QHBoxLayout()
        self.playButton = QPushButton()
        self.stopButton = QPushButton()

        self.playButton.setIcon(self.PLAY_ICON)
        self.stopButton.setIcon(self.STOP_ICON)

        self.playButton.clicked.connect(self.playSong)
        self.stopButton.clicked.connect(self.stopSong)
        
        horizontalLayout7.addStretch(1)
        horizontalLayout7.addWidget(self.playButton)
        horizontalLayout7.addWidget(self.stopButton)
        horizontalLayout7.addStretch(1)


        horizontalLayout8 = QHBoxLayout()
        self.saveButton = QPushButton()
        self.saveButton.setText("Save")
        self.saveButton.clicked.connect(self.saveSong)
        
        horizontalLayout8.addStretch(1)
        horizontalLayout8.addWidget(self.saveButton)

        mainLayout.addLayout(horizontalLayout1)
        mainLayout.addLayout(horizontalLayout2)
        mainLayout.addWidget(self.styleGroupBox)
        mainLayout.addLayout(horizontalLayout3)
        mainLayout.addLayout(horizontalLayout4)
        mainLayout.addWidget(self.descriptionTextEdit)
        mainLayout.addLayout(horizontalLayout5)
        mainLayout.addLayout(horizontalLayout6)
        mainLayout.addLayout(horizontalLayout7)
        mainLayout.addLayout(horizontalLayout8)

    def clearForm(self):
        self.titleEdit.clear()
        self.statusBox.clear()
        for widget in self.styleGroupBox.children():
            if not isinstance(widget, QGridLayout):
                widget.deleteLater()

        self.durationLine.clear()
        self.projectComboBox.clear()
        self.variationLine.clear()
        self.descriptionTextEdit.clear()
        self.locationLine.clear()

    def changePage(self, index):
        title = self.songsListWidget.item(index).data(Qt.UserRole)
        self.clearForm()
        self.populateForm(title)
        self.slider.setValue(0)

    def populateForm(self, title): #title is the primary key
        listArray = queries("""SELECT title, status, style, duration, description,
        location, project, variation_another_song, timestamp from songs WHERE title = ?""", (title,))
        print(listArray)
        if len(listArray) != 0:
            title = listArray[0][0]
            status = listArray[0][1]
            
            styles = []
            styleArray = listArray[0][2]
            if styleArray != None:
                if ",,," in styleArray:
                    styles = styleArray.split(",,,")
                else:
                    styles.append(styleArray)
            duration = listArray[0][3]
            description = listArray[0][4]
            location = listArray[0][5]
            project = listArray[0][6]
            variation_another_song = listArray[0][7]
            timestamp = listArray[0][8]
        else:
            title = None
            status = None
            styles = None
            duration = None
            description = None
            location = None
            project = None
            variation_another_song = None
            timestamp = None

        if title != None: self.titleEdit.setText(title)

        self.statusBox.addItems(["Select...", "Demo", "WIP", "Idea", "Unfinished song", "EQ", "Master", "Finished"])
        if status != None: self.statusBox.setCurrentText(status)
        if timestamp != None: self.dateEdit.setDateTime(datetime.strptime(timestamp, '%d/%m/%Y %H:%M'))
        else: self.dateEdit.setDateTime(datetime.now())#default

        styleArray = queries("select style from songs where style is not null")
        
        """
        print(styleArray)
        if styleArray != None:
            styleArray = styleArray[0][0]
            if ",,," in styleArray:
                styles = styleArray.split(",,,")
            else:
                styles.append(styleArray)"""

        stylesArray = []
        
        query = queries("select style from songs where style is not null")
        if len(query) != 0:
            for style in query:
                stylesMiniArray = style[0].split(",,,")
                stylesMiniArray = list(filter(None, stylesMiniArray))
                for item in stylesMiniArray:
                    if item not in stylesArray:
                        print(item, "la puta de horos")
                        if item != '':
                            stylesArray.append(item)

        self.x = 0
        self.y = 0

        if len(stylesArray) != 0:
            for style in stylesArray:
                    print("style", style)
                    checkBox = QCheckBox(style)
                    self.styleLayout.addWidget(checkBox, self.x, self.y)
                    self.checkBoxPositionAsignment()
                    print("here")
        self.addStyle()

        if styles!= None:
            if len(styles) != 0: 
                print("fukcing sytles", styles)
                for style in styles:
                    for checkbox in self.styleGroupBox.children():
                        if isinstance(checkbox, QCheckBox):
                            if checkbox.text() == style:
                                checkbox.setChecked(True)

        if duration != None:
                time = QTime(0,0,0)
                self.durationLine.setTime(time.addSecs(duration))
        
        projectsArray = ["Select..."]
        projectsArrayQuery = queries("SELECT project from songs")
        if len(projectsArrayQuery) != 0:
            for project in projectsArrayQuery[0]:
                if project not in projectsArray:
                    projectsArray.append(project)
        if project != None: self.projectComboBox.setCurrentText(project)

        if variation_another_song != None: self.variationLine.setText(variation_another_song)
        if description != None: self.descriptionTextEdit.setText(description)
        
        available = False
        if location != None: 
            self.locationLine.setText(location)
        if len(self.locationLine.text()) != 0:
            try:
                self.playlist = QMediaPlaylist()
                self.playlist.addMedia(QMediaContent(QUrl.fromLocalFile(location)))
                self.mediaPlayer.setPlaylist(self.playlist)
            except:
                pass
            available = True#I know this is stupid but just in case

        self.slider.setVisible(available)
        self.playButton.setVisible(available)
        self.stopButton.setVisible(available)

    def populateList(self, locatorItem=None, locatorColumn=None):
        print(locatorItem, locatorColumn)
        self.songsListWidget.blockSignals(True)
        self.songsListWidget.clear()
        if locatorItem == None or locatorItem == "": 
            listArray = queries("""SELECT title, status, timestamp from songs """)
            print(listArray)
        else:
            if locatorColumn != "All": #No strings concatenation, no security holes
                if locatorColumn == "Title": 
                    sql = """SELECT title, status, timestamp from songs where title LIKE ?"""
                elif locatorColumn == "Status": 
                    sql = """SELECT title, status, timestamp from songs where status LIKE ?"""
                elif locatorColumn == "Description": 
                    sql = """SELECT title, status, timestamp from songs where description LIKE ?"""
                elif locatorColumn == "Style": 
                    sql = """SELECT title, status, timestamp from songs where style LIKE ?"""

                locatorItem = "%" + locatorItem + "%"
                listArray = queries(sql, (locatorItem,))
            else:
                locatorItem = "%" + locatorItem + "%"
                variables = [locatorItem, locatorItem, locatorItem, locatorItem, locatorItem]
                listArray = queries("""SELECT title, status, timestamp from songs 
                where title LIKE ? OR type LIKE ? OR original_song LIKE ? OR link LIKE ? 
                OR description LIKE ?""", variables)
        for item in listArray:
            title = item[0]
            status = item[1]
            timestamp = item[2]
            try:
                timestamp = datetime.strptime(timestamp, "%d/%m/%Y %H:%M")
                timestamp = timestamp.strftime("%d/%m/%Y")
            except:
                timestamp = ""

            text = "%s %s %s" % (title, status, timestamp)
            qItem = QListWidgetItem(text)
            qItem.setData(Qt.UserRole, title)
            self.songsListWidget.addItem(qItem)
        #new idea
        qItem = QListWidgetItem("New song...")
        qItem.setData(Qt.UserRole, "New song...") #otherwise that would be an error
        self.songsListWidget.addItem(qItem)
        self.songsListWidget.blockSignals(False)

    def songVariations(self):
        sql = "SELECT title from songs"
        songArray = []
        for song in queries(sql)[0]:
            songArray.append(song)
        return songArray
    def checkBoxPositionAsignment(self):
            self.y += 1
            if self.y == 4:
                self.y = 0 
                self.x += 1
    def addStyle(self, text=""):
        "text = "" if comes from outside"

        styleEdit = QLineEdit()
        styleEdit.setPlaceholderText("Style")
        styleEdit.returnPressed.connect(lambda:self.addStyle(styleEdit.text()))

        if text != "":
            self.styleLayout.takeAt(self.styleLayout.count()-1).widget().deleteLater()

            styleCheckBox = QCheckBox()
            styleCheckBox.setText(text)
            print(text)
            self.styleLayout.addWidget(styleCheckBox, self.x, self.y)
            self.checkBoxPositionAsignment()
            print(self.durationLine.text())
        self.styleLayout.addWidget(styleEdit)


    def checkSong(self, widget):
        text = widget.text()
        sql = "SELECT title from songs where title = %s"
        if len(queries(sql, (text,))) != 0:
            widget.setText("")
            
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
        print(position, self.mediaPlayer.duration(), "hoy")
        if position != self.mediaPlayer.duration():
            self.slider.setValue(position)
    def durationChanged(self, duration):
        print(duration, self.mediaPlayer.position(), "yeha")
        if duration != self.mediaPlayer.position():
            print("duration chagned")
            self.slider.setRange(0, duration)
    def playSlider(self):
        self.mediaPlayer.setPosition(self.slider.value())

    def stopSong(self):
        self.mediaPlayer.stop()

    def locateFile(self):
        print("Here")
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

    def saveSong(self):
        title = self.titleEdit.text()
        status = self.statusBox.currentText()
        date = self.dateEdit.text()
        style = ""
        
        print(status, style)
        x = 0
        for checkBox in self.styleGroupBox.children():
            if isinstance(checkBox, QCheckBox):
                if checkBox.isChecked():
                    style += (checkBox.text()) + ",,,"
                    x+=1
        if x != 0: style = style.rstrip(",,,")
        else: style = None

        duration = self.durationLine.time()
        duration = QTime(0, 0).secsTo(duration)

        project = self.projectComboBox.currentText()
        variation = self.variationLine.text()
        description = self.descriptionTextEdit.toPlainText()
        location = self.locationLine.text()

        variables = [title, status, description, location, project,\
        variation, date, style, duration]

        print("---------", variables)

        sql = """INSERT OR REPLACE into songs 
        (title, status, description, location, project,
        variation_another_song, timestamp, style, duration)

        values 
        (?,      ?,       ?,          ?,     ?,
         ?,                     ?,         ?,      ?)"""

        print("I'm coming!!!")
        queries(sql, variables)
        self.populateList()


if __name__ == '__main__':
    app = QApplication([])
    songList = SongList()
    songList.show()
    app.exec()



        
        

