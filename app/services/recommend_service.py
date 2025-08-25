import pickle
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("TMBD_API_Key")

# تحميل البيانات
movies = pickle.load(open("Move-recommendation-system/models/movies.pkl", "rb"))
similarity = pickle.load(open("Move-recommendation-system/models/similarity.pkl", "rb"))

def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    res = requests.get(url)
    data = res.json()
    path = data.get("poster_path")
    return f'https://image.tmdb.org/t/p/w500{path}' if path else ""

def fetch_trailer(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}&language=en-US'
    res = requests.get(url)
    for video in res.json().get("results", []):
        if video['type'] == "Trailer" and video["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def recommend(movie_title: str, genre: str = "All"):
    try:
        index = movies[movies['title'].str.lower() == movie_title.lower()].index[0]
    except IndexError:
        return {"titles": [], "posters": [], "ratings": [], "trailers": []}

    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:]

    titles, posters, ratings, trailers = [], [], [], []
    for i in movie_list:
        movie = movies.iloc[i[0]]
        if genre != "All" and genre not in movie["genres"]:
            continue

        movie_id = movie["id"]
        titles.append(movie["title"])
        posters.append(fetch_poster(movie_id))
        ratings.append(movie.get("vote_average", "N/A"))
        trailers.append(fetch_trailer(movie_id))

        if len(titles) == 5:
            break

    return {
        "titles": titles,
        "posters": posters,
        "ratings": ratings,
        "trailers": trailers
    }