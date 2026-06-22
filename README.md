# StockAnalyzer API

API REST en FastAPI para consultar precios y análisis técnico (SMAs) de tickers vía Yahoo Finance.

## Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/v1/ticker/{symbol}` | Precio de cierre actual |
| GET | `/api/v1/ticker/{symbol}/analysis` | Indicadores técnicos (SMA8/21/50/100) + serie de cierres |
| GET | `/api/v1/ticker/{symbol}/chart.png` | Gráfico PNG con cierre + SMAs superpuestas |
| GET | `/docs` | Swagger UI interactivo |

### Parámetro `period`

`/analysis` y `/chart.png` aceptan `?period=` con valores de Yahoo Finance: `1mo`, `3mo` (default), `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`.

### Ejemplos

```bash
curl http://127.0.0.1:8000/api/v1/ticker/AAPL
# {"symbol":"AAPL","current_price":298.01}

curl 'http://127.0.0.1:8000/api/v1/ticker/AAPL/analysis?period=6mo'
# {"symbol":"AAPL","period":"6mo","points":124,"sma_last":{"SMA8":..., "SMA100":274.5486}, ...}

curl -o chart.png 'http://127.0.0.1:8000/api/v1/ticker/AAPL/chart.png?period=6mo'
```

### Respuestas de error

- `404` — ticker no encontrado o sin datos en el periodo
- `500` — error inesperado del proveedor

## Stack

- Python 3.13 + FastAPI 0.138 + yfinance 1.4 + matplotlib 3.11
- Servidor: uvicorn
- Imagen base Docker: `python:3.13-slim`, usuario non-root

## Run local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://127.0.0.1:8000
```

## Run con Podman

```bash
podman build -t stockanalyzer-gitops:local .
podman run -d --name stockanalyzer -p 8000:8000 stockanalyzer-gitops:local
# o desde el registry:
podman run -d --name stockanalyzer -p 8000:8000 ghcr.io/mas26-grupo4/stockanalyzer-gitops:v1.3.0
```

## Estructura

```
app/
├── main.py              # FastAPI() + include_router
├── routers/
│   ├── ticker.py        # /api/v1/ticker/{symbol}
│   └── analysis.py      # /analysis y /chart.png
└── services/
    ├── yfinance_service.py  # precio actual
    ├── analysis_service.py  # descarga histórico + SMAs
    └── chart_service.py     # render PNG con matplotlib
```

Patrón: router (HTTP) no importa yfinance; service (datos) no importa FastAPI. Swappear proveedor = editar solo `services/`.

## Versiones

- `v1.0.0` — endpoint básico `/api/v1/ticker/{symbol}`
- `v1.1.0` — contenerización (Containerfile + podman-compose)
- `v1.2.0` — endpoints de análisis y gráfico (3 meses fijo)
- `v1.3.0` — periodo configurable vía `?period=`
