import streamlit as st
import pickle
import pandas as pd
import requests
import random

def get_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=e5acd5ea13ebce8c7a5c39426e5a1434&language=en-US".format(
        movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data.get('poster_path', 'default_path_to_use_if_missing')
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def get_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=e5acd5ea13ebce8c7a5c39426e5a1434&language=en-US"
    response = requests.get(url)
    data = response.json()
    if 'results' in data:
        trailers = [video['key'] for video in data['results'] if video['type'] == 'Trailer']
        if trailers:
            return trailers[0]
    return None

def recommend_by_genre(genre):
    movies_filtered = movies_data[movies_data['genres'].str.contains(genre)]
    movies_filtered_titles = movies_filtered['title'].tolist()
    movies_filtered_indexes = [movies[movies['title'] == title].index[0] for title in movies_filtered_titles]
    similarity_filtered = similarity[movies_filtered_indexes]

    movies_list = sorted(list(enumerate(similarity_filtered.max(axis=0))), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_tmdb_links = []
    recommended_movies_trailers = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)

        recommended_movies_posters.append(get_poster(movie_id))

        tmdb_link = f"https://www.themoviedb.org/movie/{movie_id}"
        recommended_movies_tmdb_links.append(tmdb_link)

        trailer = get_trailer(movie_id)
        if trailer:
            trailer_link = f"https://www.youtube.com/watch?v={trailer}"
            recommended_movies_trailers.append(trailer_link)
        else:
            recommended_movies_trailers.append(None)

    combined_recommendations = list(zip(recommended_movies, recommended_movies_posters, recommended_movies_tmdb_links, recommended_movies_trailers))
    random.shuffle(combined_recommendations)
    recommended_movies, recommended_movies_posters, recommended_movies_tmdb_links, recommended_movies_trailers = zip(*combined_recommendations)

    return recommended_movies, recommended_movies_posters, recommended_movies_tmdb_links, recommended_movies_trailers

def recommend_by_movie(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies = []
    recommended_movies_posters = []
    recommended_movies_tmdb_links = []
    recommended_movies_trailers = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)

        recommended_movies_posters.append(get_poster(movie_id))

        tmdb_link = f"https://www.themoviedb.org/movie/{movie_id}"
        recommended_movies_tmdb_links.append(tmdb_link)

        trailer = get_trailer(movie_id)
        if trailer:
            trailer_link = f"https://www.youtube.com/watch?v={trailer}"
            recommended_movies_trailers.append(trailer_link)
        else:
            recommended_movies_trailers.append(None)

    return recommended_movies, recommended_movies_posters, recommended_movies_tmdb_links, recommended_movies_trailers

movies_dict = pickle.load(open('movies_dict1.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity1.pkl', 'rb'))

@st.cache_resource
def load_movie_data():
    return pd.read_csv('tmdb_5000_movies.csv')

movies_data = load_movie_data()

def get_movie_details(movie_name):
    movie_details = movies_data[movies_data['title'] == movie_name]
    genres_list = eval(movie_details['genres'].iloc[0])
    genres = ', '.join([genre['name'] for genre in genres_list])
    movie_details['genres'] = genres
    return movie_details[['genres', 'overview', 'release_date', 'vote_average']]

background_image = 'https://preview.redd.it/how-can-someone-make-this-background-with-html-and-css-i-v0-zjgs096khv591.jpg?auto=webp&s=9659527da9196c27a8875200b41d20a8e901c341'

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("{background_image}");
        background-size: cover;
    }}
    .stText, .stTitle, .stMarkdown {{
        color: white;  
    }}
    .movie-details-container {{
        background-color: rgba(255, 255, 255, 0.7);
        padding: 20px;  
        border-radius: 10px;
        margin-top: 20px;
        margin-bottom: 20px;
        width: 100%; 
        box-sizing: border-box;
        display: flex;
        align-items: center; 
    }}
    .movie-title, .movie-info {{
        background-color: rgba(0, 0, 0, 0.5);
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }}
    .movie-info p {{
        margin: 5px 0; 
    }}
    .poster {{
        width: 50%; 
        margin: 0 auto; 
        display: block; 
    }}
    .details {{
        width: 50%; 
    }}
    .radio-item label {{
        font-size: 20px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<h1 style="color: white; text-align: center;">Movie Recommender System</h1>', unsafe_allow_html=True)

st.markdown('<p style="color: white; text-align: center;">Select how you want to explore movies:</p>', unsafe_allow_html=True)
recommendation_type = st.radio("Choose Recommendation Type:", ("By Movie", "By Genre"), index=0, key="radio")
if recommendation_type == "By Movie":
    selected_movie_name = st.selectbox('Select a movie:', movies['title'].values)
    if st.button('Recommend'):
        recommended_movies, recommended_movies_posters, recommended_movies_tmdb_links, recommended_movies_trailers = recommend_by_movie(
            selected_movie_name)

        for i in range(0, len(recommended_movies), 2):
            st.markdown('<div class="row-container">', unsafe_allow_html=True)
            for j in range(2):
                index = i + j
                if index < len(recommended_movies):
                    movie = recommended_movies[index]
                    poster = recommended_movies_posters[index]
                    movie_details = get_movie_details(movie)
                    tmdb_link = recommended_movies_tmdb_links[index]
                    trailer_link = recommended_movies_trailers[index]

                    st.markdown('<div class="column">', unsafe_allow_html=True)  # Start column for movie
                    st.markdown(
                        f'<div class="movie-details-container"><h2 class="movie-title">Movie {index + 1}: {movie}</h2></div>',
                        unsafe_allow_html=True)
                    st.image(poster, width=250, use_column_width=False, caption=f"Poster for {movie}")
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><strong>Genres:</strong> {movie_details["genres"].values[0]}</p></div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><strong>Overview:</strong> {movie_details["overview"].values[0]}</p></div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><strong>Release Date:</strong> {movie_details["release_date"].values[0]}</p></div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><strong>Rating:</strong> {movie_details["vote_average"].values[0]}</p></div>',
                        unsafe_allow_html=True)
                    if trailer_link:
                        st.video(trailer_link)
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><a href="{tmdb_link}" target="_blank">View on TMDB</a></p></div>',
                        unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)  # End column for movie
            st.markdown('</div>', unsafe_allow_html=True)
else:
    selected_genre = st.selectbox('Select a genre:',
                                  ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Drama', 'Family', 'Fantasy',
                                   'History', 'Horror', 'Music', 'Mystery', 'Romance', 'Science Fiction', 'Thriller', 'War',
                                   'Western'])
    if st.button('Recommend'):
        recommended_movies, recommended_movies_posters, recommended_movies_tmdb_links, recommended_movies_trailers = recommend_by_genre(
            selected_genre)

        for i in range(0, len(recommended_movies), 2):
            st.markdown('<div class="row-container">', unsafe_allow_html=True)
            for j in range(2):
                index = i + j
                if index < len(recommended_movies):
                    movie = recommended_movies[index]
                    poster = recommended_movies_posters[index]
                    movie_details = get_movie_details(movie)
                    tmdb_link = recommended_movies_tmdb_links[index]
                    trailer_link = recommended_movies_trailers[index]

                    st.markdown('<div class="column">', unsafe_allow_html=True)  # Start column for movie
                    st.markdown(
                        f'<div class="movie-details-container"><h2 class="movie-title">Movie {index + 1}: {movie}</h2></div>',
                        unsafe_allow_html=True)
                    st.image(poster, width=250, use_column_width=False, caption=f"Poster for {movie}")
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><strong>Genres:</strong> {movie_details["genres"].values[0]}</p></div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><strong>Overview:</strong> {movie_details["overview"].values[0]}</p></div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><strong>Release Date:</strong> {movie_details["release_date"].values[0]}</p></div>',
                        unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><strong>Rating:</strong> {movie_details["vote_average"].values[0]}</p></div>',
                        unsafe_allow_html=True)
                    if trailer_link:
                        st.video(trailer_link)
                    st.markdown(
                        f'<div class="movie-details-container"><p class="movie-info"><a href="{tmdb_link}" target="_blank">View on TMDB</a></p></div>',
                        unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)  # End column for movie
            st.markdown('</div>', unsafe_allow_html=True)

