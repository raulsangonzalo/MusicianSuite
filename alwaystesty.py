import sqlite3
conn = sqlite3.connect("test.db")
c = conn.cursor()

# Create table songs

c.execute('''CREATE TABLE IF NOT EXISTS songs(
             id INTEGER PRIMARY KEY,
             title TEXT NOT NULL PRIMARY KEY,
             status TEXT, 
             description TEXT,
             location TEXT,
             project TEXT,
             variation_another_song TEXT,
             timestamp TIMESTAMP
             style TEXT[] ,
            duration int
             )''')

# Create table recorded snippets
c.execute('''CREATE TABLE IF NOT EXISTS recorded_ideas(
             id INTEGER PRIMARY KEY,
             title TEXT NOT NULL,
             type TEXT, 
             original_song TEXT,
             link TEXT,
             description TEXT,
             location TEXT,
             minute int,
             timestamp TIMESTAMP
             )''')

# Insert a row of data

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()
print("done!")