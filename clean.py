import pandas as pd

def clean_data():

    # Load the dataset
    df = pd.read_csv("data/dataset.csv")

    df = df.drop("Unnamed: 0", axis="columns")
    #print(df.shape)

    df = df.dropna()
    print(df.shape)

    genre_table = df[["track_name", "artists", "track_genre"]].drop_duplicates()
    print(genre_table.shape)

    genre_lists = genre_table.groupby(["track_name", "artists"])["track_genre"].agg(";".join).reset_index()
    genre_lists = genre_lists.rename(columns={"track_genre": "genres"})
    print(genre_lists.shape)
    print(genre_lists[genre_lists["artists"] == "All Time Low"].head())

    df = df.drop_duplicates(subset=["track_name", "artists"])
    #print(df.shape)
    df = df.merge(genre_lists, on=["track_name", "artists"])
    print(df.shape)

    df.to_csv("data/songs_clean.csv", index=False)

if __name__ == "__main__":
    clean_data()