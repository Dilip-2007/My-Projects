import streamlit as st
import numpy as np


# --------------------------------
# Page configuration
# --------------------------------
st.set_page_config(
    page_title="Smart Recommender",
    page_icon="🎬",
    layout="centered"
)


# --------------------------------
# Title
# --------------------------------
st.title("🎬 Smart Recommender Agent")

st.write(
    "Select a movie and find mathematically similar movies."
)


# --------------------------------
# Movie dataset
# --------------------------------
movies = {

    "Interstellar": {
        "vector": np.array([0.9, 1.0, 0.0, 0.1, 0.8]),
        "description": "Space, science, adventure and emotional drama."
    },

    "The Martian": {
        "vector": np.array([0.8, 0.9, 0.1, 0.0, 0.7]),
        "description": "Survival, Mars, science and adventure."
    },

    "Gravity": {
        "vector": np.array([0.9, 1.0, 0.0, 0.0, 0.5]),
        "description": "Space survival and intense science-fiction."
    },

    "Inception": {
        "vector": np.array([0.9, 0.8, 0.0, 0.1, 0.9]),
        "description": "Mind-bending science fiction and action."
    },

    "Avengers: Endgame": {
        "vector": np.array([1.0, 0.8, 0.2, 0.1, 0.8]),
        "description": "Superheroes, action and emotional drama."
    },

    "Titanic": {
        "vector": np.array([0.1, 0.0, 0.0, 1.0, 1.0]),
        "description": "Romance and emotional drama."
    },

    "The Notebook": {
        "vector": np.array([0.0, 0.0, 0.0, 1.0, 0.9]),
        "description": "Romantic emotional drama."
    },

    "Toy Story": {
        "vector": np.array([0.4, 0.1, 1.0, 0.2, 0.5]),
        "description": "Animated comedy, friendship and adventure."
    },

    "The Dark Knight": {
        "vector": np.array([1.0, 0.3, 0.0, 0.0, 0.9]),
        "description": "Superhero action and dark drama."
    },

    "Jurassic Park": {
        "vector": np.array([0.8, 0.9, 0.1, 0.0, 0.6]),
        "description": "Science fiction, adventure and survival."
    }
}


# --------------------------------
# Cosine similarity function
# --------------------------------
def cosine_similarity(vector_a, vector_b):

    numerator = np.dot(vector_a, vector_b)

    denominator = (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )

    if denominator == 0:
        return 0

    return numerator / denominator


# --------------------------------
# Movie selection
# --------------------------------
selected_movie = st.selectbox(
    "Choose a movie you like:",
    list(movies.keys())
)


# --------------------------------
# Recommendation count
# --------------------------------
number_of_recommendations = st.slider(
    "Number of recommendations:",
    min_value=1,
    max_value=5,
    value=3
)


# --------------------------------
# Recommendation button
# --------------------------------
if st.button("🔍 Find Similar Movies"):

    selected_vector = movies[selected_movie]["vector"]

    similarities = []

    for movie_name, movie_data in movies.items():

        # Don't recommend the movie itself
        if movie_name == selected_movie:
            continue

        similarity = cosine_similarity(
            selected_vector,
            movie_data["vector"]
        )

        similarities.append(
            (movie_name, similarity)
        )


    # --------------------------------
    # Sort by similarity
    # --------------------------------
    similarities.sort(
        key=lambda x: x[1],
        reverse=True
    )


    # --------------------------------
    # Display selected movie
    # --------------------------------
    st.subheader(
        f"🎯 Because you liked: {selected_movie}"
    )

    st.write(
        movies[selected_movie]["description"]
    )


    st.divider()


    # --------------------------------
    # Display recommendations
    # --------------------------------
    st.subheader("🍿 Recommended Movies")

    for rank, (movie_name, similarity) in enumerate(
        similarities[:number_of_recommendations],
        start=1
    ):

        percentage = similarity * 100

        st.write(
            f"### {rank}. {movie_name}"
        )

        st.progress(
            min(max(similarity, 0), 1)
        )

        st.write(
            f"Similarity: **{percentage:.2f}%**"
        )

        st.write(
            movies[movie_name]["description"]
        )

        st.divider()