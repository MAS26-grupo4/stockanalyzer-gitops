"""Entrypoint de la aplicación FastAPI.

Compone routers. El objeto `app` es el target de uvicorn:
    uvicorn app.main:app --reload
"""
from fastapi import FastAPI

from app.routers import ticker, analysis

app = FastAPI(title="StockAnalyzer API", version="1.2.0")
app.include_router(ticker.router)
app.include_router(analysis.router)
