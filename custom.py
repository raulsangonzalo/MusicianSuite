from PySide2.QtCore import QEvent, Qt, Signal
from PySide2.QtWidgets import QDialog


class QDialogPlus(QDialog):
    signalSpacePressed = Signal(str)

    def __init__(self, parent=None):
        super(QDialogPlus, self).__init__(parent)

    def event(self, event):
        super().event(event)
        if (event.type()==QEvent.KeyPress) and (event.key()==Qt.Key_Space):
            self.signalSpacePressed.emit("Key Space; ")
            return True
        if (event.type()==QEvent.KeyPress) and (event.key()==Qt.Key_R):
            self.signalSpacePressed.emit("Key R; ")
            return True
        else:
            return False
        #return QDialogPlus.event(self, event)
