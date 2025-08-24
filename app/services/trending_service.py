import pickle
import os
import requests
import pandas as pd
from dotenv import load_dotenv
from .recommend_service import fetch_poster, fetch_trailer

load_dotenv()
api_key = os.getenv("TMBD_API_Key")

movies = pickle.load(open("models/movies.pkl", "rb"))

def trending(genre: str = "All"):
    trending_df = movies.copy()
    if genre != "All":
        trending_df = trending_df[trending_df["genres"].apply(lambda g: genre in g)]

    top = trending_df.sort_values(by="weighted_average", ascending=False).head(10)

    titles, posters, ratings, trailers = [], [], [], []
    for _, row in top.iterrows():
        movie_id = row["id"]
        titles.append(row["title"])
        posters.append(fetch_poster(movie_id))
        ratings.append(row.get("vote_average", "N/A"))
        trailers.append(fetch_trailer(movie_id))

    return {
        "titles": titles,
        "posters": posters,
        "ratings": ratings,
        "trailers": trailers
    }