import sqlite3
from PyQt5.QtCore import QSettings

def createTables(dbname=""): #if dbname passed, that's the new
    """ Create table songs"""

    _settings = QSettings("Raul Sangonzalo", "Musician Suite")
    dbName = _settings.value("currentDatabase", "test.db")

    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS songs(
                title TEXT NOT NULL PRIMARY KEY,
                status TEXT, 
                description TEXT,
                location TEXT,
                project TEXT,
                variation_another_song TEXT,
                timestamp TIMESTAMP,
                style TEXT,
                duration int
                )''')

    # Create table recorded snippets
    c.execute('''CREATE TABLE IF NOT EXISTS recorded_ideas(
                title TEXT NOT NULL PRIMARY KEY,
                type TEXT, 
                original_song TEXT,
                link TEXT,
                description TEXT,
                location TEXT,
                minute int,
                timestamp TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def dropTables():
    #TODO QMessageBox outside

    _settings = QSettings("Raul Sangonzalo", "Musician Suite")
    dbName = _settings.value("currentDatabase", "test.db").toString()

    conn = sqlite3.connect(dbName)
    c = conn.cursor()
    c.execute('''DROP TABLE songs''')
    c.execute('''DROP TABLE recorded_ideas''')
    conn.commit()
    conn.close()

def queries(sqlstr, variables=None):  #to handle queries neatly
    _settings = QSettings("Raul Sangonzalo", "Musician Suite")
    dbName = _settings.value("currentDatabase", "test.db")
    conn = sqlite3.connect(dbName) #TODO <<read from registry to get the existing db, if not prompt to select
    c = conn.cursor()
    if variables == None: c.execute(sqlstr)
    else: c.execute(sqlstr, (variables))
    try:
        items_available = c.fetchall() # double unnest -> [][]
    except:
        items_available = None #inserts return None
    conn.commit()
    conn.close()
    return items_available

#dropTables()
#createTables()
#x = 2000
##variables = []
#while x < 2010:
#    text = """INSERT OR REPLACE into songs 
#        (title) values
#        (%s)""" % x
#    queries(text)
#    text = """INSERT OR REPLACE into recorded_ideas 
#        (title) values
#        (%s)""" % x
#    queries(text)
#    print("inserting %s" % x )
#    x+=1
