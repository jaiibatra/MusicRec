from recommend import recommend
from collab import collab_recommend


def hybrid_recommend(title, artist):
    # Try playlist-based first
    results = collab_recommend(title, artist)

    # A text message means the song isn't in any playlist, so fall back
    if isinstance(results, str):
        return "sound_based", recommend(title, artist)
    return "playlist_based", results

if __name__ == "__main__":
    for song, singer in [("Yellow", "Coldplay"),
                         ("Blinding Lights", "The Weeknd"),
                         ("Not A Real Song", "Nobody")]:
        method, results = hybrid_recommend(song, singer)
        print(f"{song}: {method}")
        print(results)
        print()