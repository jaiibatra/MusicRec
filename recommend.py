import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

conn = sqlite3.connect("data/music.db")
df = pd.read_sql("SELECT * FROM songs", conn)
conn.close()

feature_cols = ["danceability", "energy", "acousticness", "valence",
                "tempo", "loudness", "speechiness", "instrumentalness"]

GENRE_BONUS = 0.035

scaler = StandardScaler()
scaled = scaler.fit_transform(df[feature_cols])


# NEW: checks whether a song shares at least one genre with the input song
def shares_genre(song_genres, input_genres):
    return len(set(song_genres.split(";")) & input_genres) > 0


def recommend(title, artist):
    matches = df[(df["track_name"].str.lower() == title.strip().lower()) &
                 (df["artists"].str.lower() == artist.strip().lower())]

    if matches.empty:
        return "This song is not in the data"

    idx = matches.index[0]

    # CHANGED: get ALL of the input song's genres, as a set
    input_genres = set(df.loc[idx, "genres"].split(";"))

    scores = cosine_similarity(scaled[idx:idx+1], scaled)[0]

    # CHANGED: show the full genres column instead of track_genre
    results = df[["track_name", "artists", "genres"]].copy()
    results["score"] = scores

    # CHANGED: a song gets the bonus if it shares ANY genre with the input
    results["same_genre"] = results["genres"].apply(shares_genre, args=(input_genres,))
    results["score"] = results["score"] + results["same_genre"] * GENRE_BONUS

    # Remove the input song so it can't recommend itself
    results = results.drop(idx)

    results = results.sort_values("score", ascending=False).head(5)
    results = results.drop("same_genre", axis="columns")
    return results


if __name__ == "__main__":
    print(recommend("Blinding Lights", "The Weeknd"))
    print(recommend("Hold On", "Chord Overstreet"))
    print(recommend("Not A Real Song", "Nobody"))