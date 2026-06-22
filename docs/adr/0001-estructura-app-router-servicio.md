# 0001 — Estructura de la app: separación router/servicio

- Estado: Aceptada
- Fecha: 2026-06-21
- Contexto: Andamiaje inicial de la app FastAPI para StockAnalyzer.

## Contexto y problema

La versión inicial de la app concentraba toda la lógica en un único
`main.py` (handler de la ruta que importaba yfinance directamente,
parseaba el CSV y devolvía el JSON). Era difícil de probar, de extender
(sabíamos que llegarían las features de análisis en v1.2.0) y de migrar
de proveedor de datos más adelante. A medida que avanzó el diplomado
necesitamos separar la capa HTTP de la capa de datos.

## Opciones consideradas

1. App FastAPI en un solo archivo (status quo).
2. Separación router / servicio: los routers dependen solo de FastAPI;
   los servicios dependen solo del proveedor de datos. Ningún
   `app.routers` importa yfinance, y ningún `app.services` importa
   FastAPI.
3. Clean architecture / hexagonal completa con adaptadores, puertos y DTOs.

## Decisión

Opción 2. Reorganizamos el código en:

```
app/
├── main.py              # FastAPI() + include_router
├── routers/
│   ├── ticker.py        # Capa HTTP para /ticker/{symbol}
│   └── analysis.py      # Capa HTTP para /analysis y /chart.png
└── services/
    ├── yfinance_service.py
    ├── analysis_service.py
    └── chart_service.py
```

## Consecuencias

Bueno:
- Añadir `/analysis` y `/chart.png` en v1.2.0 solo tocó archivos nuevos
  en `routers/` y `services/`. No hubo que modificar `main.py` más allá
  del `include_router`.
- yfinance se puede reemplazar editando únicamente
  `services/yfinance_service.py`.
- Se pueden escribir tests contra los servicios sin levantar FastAPI.

Malo / trade-offs:
- Overhead leve para una app de un solo endpoint. Vale la pena dado el
  roadmap a v1.2.0.

Se descartó la opción 3 porque los objetivos de aprendizaje del diplomado
son Kubernetes y GitOps, no arquitectura hexagonal. La opción 2 alcanza
para demostrar separación de responsabilidades sin convertirse ella misma
en el tema.
