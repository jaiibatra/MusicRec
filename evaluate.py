import sqlite3
import pandas as pd

# Load the playlist data
conn = sqlite3.connect("data/music.db")
pt = pd.read_sql("SELECT * FROM playlist_tracks", conn)
conn.close()

pt["playlist_id"] = pt["user_id"] + "|" + pt["playlistname"]

# Split USERS 80% train / 20% test (all of a user's playlists stay together)
all_users = pd.Series(pt["user_id"].unique())
test_users = all_users.sample(frac=0.2, random_state=42)

train = pt[~pt["user_id"].isin(test_users)]
test = pt[pt["user_id"].isin(test_users)]

print(f"Test users: {len(test_users):,}")
print(f"Test playlists: {test['playlist_id'].nunique():,}")
print(f"Train rows: {len(train):,}")
print(f"Test rows: {len(test):,}")

# How many training playlists each song appears in (its popularity)
song_pop = train.groupby(["track_name", "artists"])["playlist_id"].nunique()


# Count how often each song shares a playlist with the seed song
def neighbor_counts(data, title, artist):
    is_song = (data["track_name"] == title) & (data["artists"] == artist)
    song_playlists = data.loc[is_song, "playlist_id"].unique()
    if len(song_playlists) == 0:
        return None
    neighbors = data[data["playlist_id"].isin(song_playlists) & ~is_song]
    return neighbors[["track_name", "artists"]].value_counts()


# Rank songs, penalizing popular ones by alpha (0 = no penalty)
def rank(counts, alpha, n=10):
    counts = counts[counts >= 2]
    scores = counts / (song_pop[counts.index] ** alpha)
    return list(scores.sort_values(ascending=False).head(n).index)


# Baseline: just recommend the most popular songs to everyone
popular = list(train[["track_name", "artists"]].value_counts().head(11).index)

# Test on 500 random test playlists with at least 5 songs
sizes = test["playlist_id"].value_counts()
eval_ids = pd.Series(sizes[sizes >= 5].index).sample(n=500, random_state=42)

alphas = [0, 0.5, 1.0]
scores = {a: [] for a in alphas}
popular_scores = []
skipped = 0

for pid in eval_ids:
    rows = test[test["playlist_id"] == pid]
    songs = list(zip(rows["track_name"], rows["artists"]))

    seed = songs[0]                  # the song we "know"
    hidden = set(songs[1:]) - {seed} # the songs we hope to find

    counts = neighbor_counts(train, seed[0], seed[1])
    if counts is None:
        skipped += 1                 # seed never appeared in training
        continue

    for a in alphas:
        recs = rank(counts, a)
        scores[a].append(len(set(recs) & hidden) / 10)

    pop_recs = [s for s in popular if s != seed][:10]
    popular_scores.append(len(set(pop_recs) & hidden) / 10)

print(f"\nPlaylists scored: {len(popular_scores)} (skipped {skipped})")
for a in alphas:
    print(f"Collaborative, alpha={a}: precision@10 = {sum(scores[a]) / len(scores[a]):.3f}")
print(f"Popularity baseline:      precision@10 = {sum(popular_scores) / len(popular_scores):.3f}")