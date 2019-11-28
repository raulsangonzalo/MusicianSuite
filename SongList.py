from PyQt5.QtWidgets import QDialog, QListWidget, QListWidgetItem, QDialog, QApplication,\
     QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QMessageBox, QStackedWidget, QLineEdit,\
     QWidget, QComboBox, QGridLayout, QCheckBox, QGroupBox, QTextEdit, QPushButton, QTimeEdit,\
     QDateTimeEdit, QCompleter
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import QTime
from datetime import datetime, timedelta
from custom import queries
import numpy as np
from functools import partial

class SongList(QWidget):
    def __init__(self, parent=None):
        super(SongList, self).__init__(parent)
        self.setupUi()
    
    def setupUi(self):
        self.setWindowTitle("Raul list of songs")
        self.mainLayout = QHBoxLayout(self)

        self.songsListWidget = QListWidget()
        
        listArray = queries("""SELECT title, status, style, duration, description,
        location, project, variation_another_song, timestamp from music.songs""")
        for item in listArray:
            
            title = item[0]
            status = item[1]
            timestamp = item[8]
            timestamp = timestamp.strftime("%d/%m/%Y")


            text = "%s %s %s" % (title, status, timestamp)
            qItem = QListWidgetItem(text)
            self.songsListWidget.addItem(qItem)
            print(title)

        self.songsListWidget.currentRowChanged.connect(self.changePage)
        self.mainLayout.addWidget(self.songsListWidget)
        self.mainLayout.addWidget(self.stackedWidget(listArray))

    def stackedWidget(self, listArray):
        self.listStackedWidget = QStackedWidget()

        x = 0
        arrayNew = [None, None, None, None, None, None, None, None, None] #only need one for validation
        listArray.append(arrayNew)
        qItem = QListWidgetItem("Add new song...")
        self.songsListWidget.addItem(qItem)
        for item in listArray:
            #items
            title = item[0]
            status = item[1]
            styles = item[2]
            duration = item[3]
            description = item[4]
            location = item[5]
            project = item[6]
            variation_another_song = item[7]
            timestamp = item[8]
            
            print(title, status, styles, duration, description, location, project, timestamp)
            #UI SETUP

            widgetPage = QWidget()
            mainLayout = QVBoxLayout(widgetPage)
            
            horizontalLayout1 = QHBoxLayout()
            titleLabel = QLabel("Song name:")
            titleEdit = QLineEdit()
            if title != None: 
                titleEdit.setText(title)
                print("hey")
            else: print("no")
            titleEdit.setAccessibleName("Title")
            titleEdit.editingFinished.connect(partial(self.checkSong, titleEdit))

            horizontalLayout1.addWidget(titleLabel)
            horizontalLayout1.addWidget(titleEdit)

            horizontalLayout2 = QHBoxLayout()
            statusLabel = QLabel("Status:")
            statusBox = QComboBox()
            statusBox.addItems(["Select...", "Demo", "WIP", "Idea", "Unfinished song", "EQ", "Master", "Finished"])
            if status != None: statusBox.setCurrentText(status)
            statusBox.setAccessibleName("Status")
            dateLabel = QLabel("Date:")
            dateEdit = QDateTimeEdit()
            dateEdit.setCalendarPopup(True)
            dateEdit.setAccessibleName("Date")
            if timestamp != None: dateEdit.setDateTime(timestamp)
            else: dateEdit.setDateTime(datetime.now())#default

            horizontalLayout2.addWidget(statusLabel)
            horizontalLayout2.addWidget(statusBox)
            horizontalLayout2.addStretch(1)
            horizontalLayout2.addWidget(dateLabel)
            horizontalLayout2.addWidget(dateEdit)

            styleLabel = QLabel("Style:")
            styleEdit = QLineEdit()

            stylesArray = queries("select style from music.songs")[0][0]
            print(stylesArray)

            self.x = 0
            self.y = 0
            styleGroupBox = QGroupBox()
            styleGroupBox.setTitle("Style:")
            styleGroupBox.setAccessibleName("Style")
            self.styleLayout = QGridLayout(styleGroupBox)
            for style in stylesArray:
                checkBox = QCheckBox(style)
                self.styleLayout.addWidget(checkBox, self.x, self.y)
                self.checkBoxPositionAsignment()
            self.addStyle()
            
            
            if styles != None: 
                for style in styles:
                    for checkbox in styleGroupBox.children():
                        if isinstance(checkbox, QCheckBox):
                            if checkbox.text() == style:
                                checkbox.setChecked(True)

            
            horizontalLayout3 = QHBoxLayout()
            durationLabel = QLabel("Duration:")
            self.durationLine = QTimeEdit()
            self.durationLine.setDisplayFormat("mm:ss")
            self.durationLine.setAccessibleName("Duration")
            if duration != None:
                time = QTime(0,0,0)
                self.durationLine.setTime(time.addSecs(duration))
            projectLabel = QLabel("Project")

            #in a function to retrieve existing
            projectsArray = ["Select..."]
            for project in queries("SELECT project from music.songs")[0]:
                if project not in projectsArray:
                    projectsArray.append(project)
            

            projectComboBox = QComboBox()
            projectComboBox.addItems(projectsArray)
            projectComboBox.setAccessibleName("Project")
            projectComboBox.setEditable(True)
            if project != None:
                projectComboBox.setCurrentText(project)
            
            horizontalLayout3.addWidget(durationLabel)    
            horizontalLayout3.addWidget(self.durationLine)
            horizontalLayout3.addWidget(projectLabel)
            horizontalLayout3.addWidget(projectComboBox)

            horizontalLayout4 = QHBoxLayout()
            descriptionLabel = QLabel("Description:")
            variationLabel = QLabel("Variation from another song: ")
            variationLine = QLineEdit()
            if variation_another_song != None:
                variationLine.setText(variation_another_song)
            completer = QCompleter(self.songVariations())
            variationLine.setCompleter(completer)
            variationLine.setAccessibleName("Variation")

            horizontalLayout4.addWidget(descriptionLabel)
            horizontalLayout4.addStretch(1)
            horizontalLayout4.addWidget(variationLabel)
            horizontalLayout4.addWidget(variationLine)

            descriptionTextEdit = QTextEdit()
            if description != None: descriptionTextEdit.setText(description)
            descriptionTextEdit.setAccessibleName("Description")

            horizontalLayout5 = QHBoxLayout()
            locationLabel = QLabel("Location:")
            locationLine = QLineEdit()
            if location != None: locationLine.setText(location)
            locationLine.setAccessibleName("Location")
            locationButton = QPushButton("...")

            horizontalLayout5.addWidget(locationLabel)
            horizontalLayout5.addWidget(locationLine)
            horizontalLayout5.addWidget(locationButton)

            horizontalLayout6 = QHBoxLayout()
            saveButton = QPushButton()
            saveButton.setText("Save")
            saveButton.clicked.connect(partial(self.saveSong, widgetPage))
            
            horizontalLayout6.addStretch(1)
            horizontalLayout6.addWidget(saveButton)

            mainLayout.addLayout(horizontalLayout1)
            mainLayout.addLayout(horizontalLayout2)
            mainLayout.addWidget(styleGroupBox)
            mainLayout.addLayout(horizontalLayout3)
            mainLayout.addLayout(horizontalLayout4)
            mainLayout.addWidget(descriptionTextEdit)
            mainLayout.addLayout(horizontalLayout5)
            mainLayout.addLayout(horizontalLayout6)


            """TODO
            
            ADD A "New Song" in the list Widget permanently,
            so form will always be editing an "existing" one instead of creating
            to make it more simple.

            checkboxes order by the amount of times they have been used.

            validation to check if song already exists

            when choose location of the song, copy the song to another folder
            if song does not exist in either of both locations, prompt to define again.

            add button to remove song, specify reason (add it to a field and have a different select query)
            
            """
            

            x=+1

            self.listStackedWidget.addWidget(widgetPage)
        return self.listStackedWidget

    def changePage(self, index):
        self.listStackedWidget.setCurrentIndex(index)
        self.songsListWidget.currentRowChanged.disconnect(self.changePage)
        self.songsListWidget.setCurrentRow(index)
        self.songsListWidget.currentRowChanged.connect(self.changePage)

    def songVariations(self):
        sql = "SELECT title from music.songs"
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
        sql = "SELECT title from music.songs where title = %s"
        if len(queries(sql, (text,))) != 0:
            widget.setText("")
            
    def saveSong(self, widgetPage):
        title = ""
        status = ""
        date = ""
        style = []
        duration = ""
        project = ""
        variation = ""
        description = ""
        location = ""
        print("gettingh ere")

        for widget in widgetPage.children():
            print(widget)
            if not isinstance(widget, (QHBoxLayout, QVBoxLayout)):
                if widget.accessibleName() == "Title": title = widget.text()
                elif widget.accessibleName() == "Status":  status = widget.currentText() #Combo Bo 
                elif widget.accessibleName() == "Date":  date = widget.text()#Date 
                elif widget.accessibleName() == "Style": 
                    for checkBox in widget.children():
                        if isinstance(checkBox, QCheckBox):
                            print("one fo this days", checkBox)
                            if checkBox.isChecked():
                                style.append(checkBox.text()) 
                elif widget.accessibleName() == "Duration": 
                    time = widget.time()
                    duration = QTime(0, 0).secsTo(time)
                elif widget.accessibleName() == "Project":  project = widget.currentText()#QComboBo 
                elif widget.accessibleName() == "Variation":  variation = widget.text()#QLineEdi 
                elif widget.accessibleName() == "Description":  description = widget.toPlainText()#QTextEdi 
                elif widget.accessibleName() == "Location":  location = widget.text()#QLineEdit

        variables = [title, status, description, location, project,\
        variation, date, style, duration]

        print("---------", variables)



        sql = """INSERT into music.songs 
        (title, status, description, location, project,
        variation_another_song, timestamp, style, duration)

        values 
        (%s,      %s,       %s,          %s,     %s,
         %s,                     %s,         %s,      %s)

        ON CONFLICT ON CONSTRAINT songs_pkey do update set title=EXCLUDED.title, status=EXCLUDED.status, 
        description=EXCLUDED.description, location=EXCLUDED.location, 
        project=EXCLUDED.project, variation_another_song=EXCLUDED.variation_another_song, 
        timestamp=EXCLUDED.timestamp, style=EXCLUDED.style, duration=EXCLUDED.duration"""
        queries(sql, variables)



if __name__ == '__main__':
    app = QApplication([])
    songList = SongList()
    songList.show()
    app.exec()



        
        

