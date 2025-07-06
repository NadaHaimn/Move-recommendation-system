import streamlit as st
import pandas as pd
import pickle
import requests
import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()
api_key = os.getenv("TMBD_API_Key")

# تحميل البيانات
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


# دالة جلب البوستر والتقييم
def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    rating = data.get('vote_average', 'N/A')

    if poster_path:
        poster_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
    else:
        poster_url = 'https://via.placeholder.com/500x750.png?text=No+Poster+Available'

    return poster_url, rating

# دالة جلب رابط التريلر
def fetch_trailer_url(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}&language=en-US'
    response = requests.get(url)
    data = response.json()
    for video in data.get('results', []):
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

# دالة التوصية
def recommend(movie, selected_genre):
    try:
        index = movies[movies['title'].str.lower() == movie.lower()].index[0]
    except IndexError:
        return [], []

    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_data = movies.iloc[i[0]]
        if selected_genre != "All" and selected_genre not in movie_data["genres"]:
            continue
        movie_id = movie_data["id"]
        recommended_movies.append(movie_data["title"])
        poster, rating = fetch_poster(movie_id)
        recommended_posters.append((poster, rating))
        if len(recommended_movies) == 5:
            break

    return recommended_movies, recommended_posters

# إعداد شكل الصفحة
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# تنسيق الواجهة
st.markdown("""
    <style>
        .main {
            display: flex;
            justify-content: center;
        }
        .block-container {
            width: 100%;
            max-width: 1150px;
            padding-top: 80px;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# عنوان الصفحة
st.markdown("<h1 style='text-align: center;'> Movie Recommendation System 🎬</h1>", unsafe_allow_html=True)
st.markdown("")
# خلفية بصورة مع طبقة شفافة حسب الوضع الليلي أو النهاري
st.markdown("""
    <style>
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1524985069026-dd778a71c7b4?auto=format&fit=crop&w=1740&q=80");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }

        @media (prefers-color-scheme: light) {
            .block-container {
                background-color: rgba(255, 255, 255, 0.6); /* خلفية فاتحة شفافة للـ light mode */
            }
        }
    </style>
""", unsafe_allow_html=True)

# اختيار الفيلم
movies_list = movies['title'].values
st.markdown("<p style='font-size: 25px; margin-bottom:-8px;'>🎬 Choose a movie from the list:</p>", unsafe_allow_html=True)

selected_movie = st.selectbox(
    label="",
    options=movies_list,
    index=None,
    placeholder="Search or choose a movie first...",
)

# زر الفلتر قبل زر Show Recommendations
with st.expander("🎯 Filter", expanded=False):
    genre_options = ["All"] + sorted({genre for sublist in movies["genres"] for genre in sublist})
    selected_genre = st.selectbox("Select Genre", options=genre_options, key="genre_filter")

# عرض التوصيات
recommendation_placeholder = st.empty()

# زر التوصيات
if st.button('🎥 Show Recommendations'):
    if not selected_movie:
        st.error("⚠️ Please select a movie first.")
    else:
        names, posters = recommend(selected_movie, selected_genre)
        with recommendation_placeholder:
            if names:
                cols = st.columns(5)
                for i in range(len(names)):
                    with cols[i]:
                        movie_id = movies[movies['title'] == names[i]]['id'].values[0]
                        movie_url = f"https://www.themoviedb.org/movie/{movie_id}"
                        poster, rating = posters[i]

                        st.markdown(f"<h5 style='text-align: center;'>{names[i]}</h5>", unsafe_allow_html=True)

                        st.markdown(f"""
                            <div style='text-align: center;margin-top: 20px;'>
                                <a>
                                    <img src='{poster}' style='border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);'>
                                </a>
                            </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"<p style='text-align: center;margin-top: 8px;'>⭐️ Ratings: {rating}</p>", unsafe_allow_html=True)

                        trailer_url = fetch_trailer_url(movie_id)
                        if trailer_url:
                            st.markdown(f"""
                                <div style='text-align: center; margin-top: 1px; margin-bottom: 30px;'>
                                    <a href='{trailer_url}' target='_blank' style='
                                        background-color: #e50914;
                                        color: white;
                                        padding: 6px 14px;
                                        text-decoration: none;
                                        border-radius: 6px;
                                        font-size: 13px;
                                        display: inline-block;
                                    '>🎞 Watch Trailer</a>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.error("⚠️ No recommendations found for this movie. Please try another one.")

# عرض قائمة Top Trending في البداية
if not selected_movie:
    st.markdown("<h3 style='margin-top:50px;'>🔥 Top Trending Movies</h3>", unsafe_allow_html=True)

    trending = movies.copy()
    if selected_genre != "All":
        trending = trending[trending["genres"].apply(lambda genres: selected_genre in genres)]

    trending_movies = trending.sort_values(by='weighted_average', ascending=False).head(10)

    cols = st.columns(5)
    for i in range(len(trending_movies)):
        with cols[i % 5]:
            movie = trending_movies.iloc[i]
            movie_id = movie['id']
            title = movie['title']
            poster, rating = fetch_poster(movie_id)

            st.markdown(f"<h5 style='text-align: center;'>{title}</h5>", unsafe_allow_html=True)

            st.markdown(f"""
                <div style='text-align: center;margin-top: 20px;'>
                    <a>
                        <img src='{poster}' style='border-radius: 10px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.6);'>
                    </a>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<p style='text-align: center;margin-top: 8px;'>⭐️ Ratings: {rating}</p>", unsafe_allow_html=True)

            trailer_url = fetch_trailer_url(movie_id)
            if trailer_url:
                st.markdown(f"""
                    <div style='text-align: center; margin-top: 1px; margin-bottom: 30px;'>
                        <a href='{trailer_url}' target='_blank' style='
                            background-color: #e50914;
                            color: white;
                            padding: 6px 14px;
                            text-decoration: none;
                            border-radius: 6px;
                            font-size: 13px;
                            display: inline-block;
                        '>🎞 Watch Trailer</a>
                    </div>
                """, unsafe_allow_html=True)
                