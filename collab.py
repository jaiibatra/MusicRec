import sqlite3
import pandas as pd

# Load the playlist data once
conn = sqlite3.connect("data/music.db")
pt = pd.read_sql("SELECT * FROM playlist_tracks", conn)
conn.close()

# One ID per playlist (user + playlist name)
pt["playlist_id"] = pt["user_id"] + "|" + pt["playlistname"]


def collab_recommend(title, artist, n=5):
    # True for every row that is the input song (ignoring case and spaces)
    is_song = ((pt["track_name"].str.lower() == title.strip().lower()) &
               (pt["artists"].str.lower() == artist.strip().lower()))

    song_rows = pt[is_song]
    if song_rows.empty:
        return "This song isn't in any playlist"

    # Every playlist that contains the song
    song_playlists = song_rows["playlist_id"].unique()

    # Every OTHER song in those playlists
    neighbor_rows = pt[pt["playlist_id"].isin(song_playlists) & ~is_song]

    # Count how often each song appears alongside the input song
    counts = neighbor_rows[["track_name", "artists"]].value_counts()

    # Turn the top n into a clean table
    results = counts.head(n).reset_index()
    results.columns = ["track_name", "artists", "playlists_together"]
    return results


if __name__ == "__main__":
    print(collab_recommend("Yellow", "Coldplay"))
    print(collab_recommend("Blinding Lights", "The Weeknd"))
    print(collab_recommend("Not A Real Song", "Nobody"))