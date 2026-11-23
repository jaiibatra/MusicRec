from load_db import load_data
from clean import clean_data

if __name__ == "__main__":
    print("Step 1: Cleaning data... ")
    clean_data()

    print("Step 2: Loading data... ")
    load_data()

    print("Pipeline complete")