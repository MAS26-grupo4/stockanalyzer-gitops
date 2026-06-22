"""Servicio de análisis técnico sobre series de Yahoo Finance.

Encapsula la descarga de histórico y el cálculo de indicadores (SMAs).
Los routers consumen este módulo; nunca importan yfinance directamente.
"""
import pandas as pd
import yfinance as yf


PERIOD_DEFAULT = "3mo"
SMA_WINDOWS = (8, 21, 50, 100)


def fetch_history(symbol: str, period: str = PERIOD_DEFAULT) -> pd.DataFrame:
    """Descarga el histórico de cierres para el periodo indicado."""
    ticker = yf.Ticker(symbol)
    return ticker.history(period=period)


def compute_indicators(history: pd.DataFrame, period: str) -> dict:
    """Calcula SMAs y devuelve el último valor de cada una junto a la serie."""
    closes = history["Close"]

    sma_last = {
        f"SMA{w}": (None if len(closes) < w else round(float(closes.rolling(window=w).mean().iloc[-1]), 4))
        for w in SMA_WINDOWS
    }

    sma_series = {
        f"SMA{w}": [None if pd.isna(v) else round(float(v), 4) for v in closes.rolling(window=w).mean().tolist()]
        for w in SMA_WINDOWS
    }

    return {
        "last_close": round(float(closes.iloc[-1]), 4),
        "period": period,
        "points": len(closes),
        "sma_last": sma_last,
        "sma_series": sma_series,
        "dates": [d.strftime("%Y-%m-%d") for d in history.index],
        "closes": [round(float(v), 4) for v in closes.tolist()],
    }


def get_analysis(symbol: str, period: str = PERIOD_DEFAULT) -> dict | None:
    """Pipeline: descarga histórico + calcula indicadores. None si no hay datos."""
    history = fetch_history(symbol, period)
    if history.empty:
        return None
    payload = compute_indicators(history, period)
    payload["symbol"] = symbol.upper()
    return payload
