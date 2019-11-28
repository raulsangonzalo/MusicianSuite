import sqlite3


def createTables():
    # Create table songs
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS songs(
                title TEXT NOT NULL PRIMARY KEY,
                status TEXT, 
                description TEXT,
                location TEXT,
                project TEXT,
                variation_another_song TEXT,
                timestamp TIMESTAMP,
                style TEXT[] ,
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
    #TODO QMessageBox
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    c.execute('''DROP TABLE songs''')
    c.execute('''DROP TABLE recorded_ideas''')
    conn.commit()
    conn.close()
def queries(sqlstr, variables=None):  #to handle queries neatly
    conn = sqlite3.connect("test.db") #TODO <<read from registry to get the existing db, if not prompt to select
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

#x = 0
#variables = []
#while x < 1000:
#    text = """INSERT OR REPLACE into recorded_ideas 
#        (title) values
#        (%s)""" % x
#    queries(text)
#    print("inserting %s" % x )
#    x+=1
