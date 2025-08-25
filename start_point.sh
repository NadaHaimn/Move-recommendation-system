#!/bin/bash

# Start FastAPI with uvicorn in the background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Streamlit
streamlit run streamlit_app/app.py --server.port=8501 --server.address=0.0.0.0
