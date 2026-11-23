import pandas as pd
import sqlite3

# Skipped ~11,027 malformed rows (under 0.1%)
playlist = pd.read_csv("data/spotify_dataset.csv", escapechar="\\", on_bad_lines="skip")
songs = pd.read_csv("data/songs_clean.csv")

playlist.columns = ["user_id", "artistname", "trackname", "playlistname"]

unique_playlists = playlist.drop_duplicates(subset=["user_id", "playlistname"])
print(f"Real playlists (user + name): {len(unique_playlists):,}")

playlist = playlist.dropna()
print(f"Playlist rows after dropping blanks: {len(playlist):,}")

songs = songs[["track_name", "artists"]].copy()
print(f"Songs in catalog: {len(songs):,}")

# --- Exact match: 872,610 rows (6.79%), 14,758 songs (18.14%) ---
print("\n=== EXACT MATCH ===")
matched = pd.merge(playlist, songs, left_on=["trackname", "artistname"], right_on=["track_name", "artists"])
percentage = (len(matched) / len(playlist)) * 100
print(f"Playlist rows matched: {len(matched):,} ({percentage:.2f}%)")

matched_songs = matched.drop_duplicates(subset=["track_name", "artists"])
matched_percentage = (len(matched_songs) / len(songs)) * 100
print(f"Catalog songs covered: {len(matched_songs):,} ({matched_percentage:.2f}%)")

#  --- Key match (case and spaces ignored) ---
playlist["track_key"] = playlist["trackname"].str.strip().str.lower()
playlist["artist_key"] = playlist["artistname"].str.strip().str.lower()
songs["track_key"] = songs["track_name"].str.strip().str.lower()
songs["artist_key"] = songs["artists"].str.strip().str.lower()

print("\n=== KEY MATCH ===")
shared_keys = songs.duplicated(subset=["track_key", "artist_key"]).sum()
print(f"Songs sharing a key (removed): {shared_keys:,}")

# Keep one song per key so the merge can't double-count playlist rows
songs = songs.drop_duplicates(subset=["track_key", "artist_key"])

matched_keys = pd.merge(playlist, songs, on=["track_key", "artist_key"])
keys_percentage = (len(matched_keys) / len(playlist)) * 100
print(f"Playlist rows matched: {len(matched_keys):,} ({keys_percentage:.2f}%)")

matched_keys_songs = matched_keys.drop_duplicates(subset=["track_key", "artist_key"])
keys_songs_percentage = (len(matched_keys_songs) / len(songs)) * 100
print(f"Catalog songs covered: {len(matched_keys_songs):,} ({keys_songs_percentage:.2f}%)")

playlist_tracks = matched_keys[["user_id", "playlistname", "track_name", "artists"]]
print(playlist_tracks.shape)

conn = sqlite3.connect("data/music.db")
playlist_tracks.to_sql("playlist_tracks", conn, if_exists="replace", index=False)
print("Loaded", len(playlist_tracks))
conn.close()