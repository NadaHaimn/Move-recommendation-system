from fastapi import APIRouter, Query
from app.services import recommend_service, trending_service

router = APIRouter()

@router.get("/recommend")
def recommend(movie_title: str = Query(...), genre: str = "All"):
    return recommend_service.recommend(movie_title, genre)

@router.get("/trending")
def trending(genre: str = "All"):
    return trending_service.trending(genre)