import sqlite3
import pandas as pd

def load_data():

    conn = None

    try:
        conn = sqlite3.connect("data/music.db")
        cursor = conn.cursor()
        df = pd.read_csv("data/songs_clean.csv")
        df.to_sql("songs", conn, if_exists="replace", index=False)
        print("Loaded", len(df), "songs into database")

    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    load_data()