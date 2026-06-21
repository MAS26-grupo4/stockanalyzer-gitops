"""Router de tickers: capa HTTP.

Solo conoce FastAPI y el servicio de yfinance. No hace I/O directo
contra proveedores externos.
"""
from fastapi import APIRouter, HTTPException

from app.services import yfinance_service

router = APIRouter(prefix="/api/v1", tags=["ticker"])


@router.get("/ticker/{symbol}")
def get_ticker_price(symbol: str):
    """Obtiene el precio actual del ticker consultando Yahoo Finance."""
    try:
        current_price = yfinance_service.get_current_price(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if current_price is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{symbol}' no encontrado o sin datos.",
        )

    return {
        "symbol": symbol.upper(),
        "current_price": round(current_price, 2),
    }
