"""Router de análisis técnico: capa HTTP."""
from fastapi import APIRouter, HTTPException, Response

from app.services import analysis_service, chart_service

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.get("/ticker/{symbol}/analysis")
def get_ticker_analysis(symbol: str):
    """Devuelve los indicadores técnicos (SMAs) de los últimos 3 meses."""
    try:
        payload = analysis_service.get_analysis(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if payload is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{symbol}' no encontrado o sin datos.",
        )

    return payload


@router.get("/ticker/{symbol}/chart.png")
def get_ticker_chart(symbol: str):
    """Devuelve un PNG con la serie de cierres y las SMAs superpuestas."""
    try:
        png_bytes = chart_service.render_chart_png(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if png_bytes is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{symbol}' no encontrado o sin datos.",
        )

    return Response(content=png_bytes, media_type="image/png")
