import psycopg2
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, pyqtSignal, QEvent

def queries(sqlstr, variables=''):
    conn = psycopg2.connect("dbname='Raul' user='postgres' host='127.0.0.1' password='R'")
    cur = conn.cursor()
    if variables == '': cur.execute(sqlstr)
    else:
        cur.execute(sqlstr, (variables))
    try:
        items_available = cur.fetchall()
    except:
        items_available = None
    conn.commit()
    cur.close()
    conn.close()
    return items_available

class QDialogPlus(QDialog):
    signalSpacePressed = pyqtSignal(str)   

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