import pandas as pd

# Load the dataset
df = pd.read_csv("data/dataset.csv")

df.info()

#print(df.isnull().sum())

#print(df[df["track_name"].isnull()])

df = df.drop("Unnamed: 0", axis="columns")
print(df.shape)

rows_with_nan = df[df.isna().any(axis=1)]
print(rows_with_nan)