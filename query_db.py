import sqlite3
import pandas as pd

conn = sqlite3.connect("data/music.db")

query = """
Select track_name, artists
From songs
Where artists LIKE '%Playboi Carti%'
"""

results = pd.read_sql(query, conn)
print(results)

conn.close()