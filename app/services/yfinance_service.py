"""Servicio de acceso a datos de mercado vía yfinance.

Capa de datos: encapsula la librería externa para que los routers
no dependan directamente de yfinance. Si se cambia el proveedor
(si yfinance cae o queremos intraday desde un broker), solo se toca este módulo.
"""
import yfinance as yf


def get_current_price(symbol: str) -> float | None:
    """Devuelve el último precio de cierre del ticker o None si no hay datos."""
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")

    if data.empty:
        return None

    return float(data["Close"].iloc[-1])
