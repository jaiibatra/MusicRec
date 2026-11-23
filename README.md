# Hybrid Music Recommender

A music recommender that combines **how songs sound** with **what real listeners put together in playlists**. Type a song or artist, pick a match, and get five recommendations in a Streamlit web app.

**Result:** 0.22 precision@10 on a user-level train/test split, about **5x** a popularity baseline.

## How it works

The app uses two recommenders and picks the right one for each song.

| | Content-based (`recommend.py`) | Collaborative (`collab.py`) |
| --- | --- | --- |
| Based on | 8 audio features (danceability, energy, tempo, ...) | Songs that appear in the same playlists |
| Method | Cosine similarity on standardized features, plus a small bonus for shared genres | Count co-occurrences across ~987K playlist entries |
| Covers | All 81,343 songs | ~16,000 songs with playlist data |
| Strength | Works for any song | Captures real taste, style, and era |

`hybrid.py` tries the collaborative recommender first. If a song has no playlist data (the cold-start problem), it falls back to the content-based one. The app shows which method it used.

Example, "Yellow" by Coldplay (playlist-based): The Scientist, Mr. Brightside, Chasing Cars, Green Eyes, Creep.

## Evaluation

`evaluate.py` holds out 20% of **users** (so no listener appears in both training and test), gives the recommender one song from each test playlist, and checks how many of its 10 recommendations are in the rest of that playlist.

| Method | Precision@10 |
| --- | --- |
| Collaborative | **0.221** |
| Popularity baseline (same top 10 for everyone) | 0.042 |

A popularity penalty was also tested and rejected: it lowered precision (0.210 at alpha 0.5, 0.077 at alpha 1.0), so the model keeps raw co-occurrence counts.

## Data pipeline

```
dataset.csv -> clean.py -> songs_clean.csv -> load_db.py -> music.db -> app
```

- **Cleaning** removes a junk index column, one blank row, and 32,656 duplicate songs.
- **Genre bias fix:** the raw data is sorted by genre, so dropping duplicates kept only the alphabetically first genre for songs listed under several (rock fell to 167 songs). Keeping every genre per song restored rock to 575, verified with SQL.
- **Playlist matching** (`explore_playlists.py`) joins 12.9M playlist rows to the catalog using lowercase, trimmed keys, recovering ~114K more rows than exact matching, and saves the result as a `playlist_tracks` table.
- `run_pipeline.py` rebuilds the song table in one command and is safe to rerun.

## Run it

**With Python:**

```
pip install -r requirements.txt
streamlit run app.py
```

**With Docker:**

```
docker build -t music-recommender .
docker run -p 8501:8501 music-recommender
```

Then open http://localhost:8501.

`data/music.db` is included, so the app runs without rebuilding anything. To rebuild from scratch, download the two datasets below into `data/`, then run `python run_pipeline.py` and `python explore_playlists.py`.

## Data sources

- [Spotify Tracks Dataset](https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset) (Kaggle): 114,000 tracks across 114 genres, with audio features
- [Spotify Playlists Dataset](https://zenodo.org/record/2594557) (University of Innsbruck, Zenodo): users, playlists, and tracks from Spotify users who shared #nowplaying tweets

## Limitations

- The catalog is a sample of about 1,000 songs per genre, so many popular songs are missing.
- The playlist data predates newer releases, so recent songs use the sound-based fallback.
- Audio features can't see language or region, so sound-based matches sometimes cross languages.

## Tech

Python, pandas, scikit-learn, SQLite, Streamlit, Docker
