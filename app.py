import streamlit as st
from recommend import df
from hybrid import hybrid_recommend

st.title("Music Recommendation")

title = st.text_input("Song title (optional)")
artist = st.text_input("Artist (optional)")

if title or artist:
    # Start with every song, then narrow down by whichever boxes are filled
    matches = df
    if title:
        matches = matches[matches["track_name"].str.contains(title, case=False, regex=False)]
    if artist:
        matches = matches[matches["artists"].str.contains(artist, case=False, regex=False)]

    if matches.empty:
        st.write("No songs found. Try a different spelling.")
    else:
        st.write(f"Found {len(matches):,} matching songs")

        # Let the user pick one of the matches
        labels = (matches["track_name"] + " — " + matches["artists"]).tolist()
        choice = st.selectbox("Pick a song", labels)
        picked = matches.iloc[labels.index(choice)]

        if st.button("Recommend"):
            method, results = hybrid_recommend(picked["track_name"], picked["artists"])
            st.info(f"Method: {method}")
            if isinstance(results, str):
                st.write(results)
            else:
                st.dataframe(results)