from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import movies

app = FastAPI(
    title="Movie Recommendation API",
    description="API for recommending and trending movies",
    version="1.0.0"
)

# السماح لـ Streamlit بالاتصال
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(movies.router, prefix="/movies", tags=["Movies"])

@app.get("/")
def root():
    return {"message": "Welcome to Movie Recommendation API 🚀"}