# 0002 — Containerfile: python:3.13-slim, usuario non-root

- Estado: Aceptada
- Fecha: 2026-06-21
- Contexto: Primera contenerización de la app FastAPI.

## Contexto y problema

Necesitábamos empaquetar la app en una imagen de contenedor para
distribuirla vía ghcr.io. Decisiones a tomar: imagen base (slim vs full
vs alpine vs distroless), si correr como root, qué tooling de Python
dejar dentro, y cómo cachear las capas de pip para que el build sea
razonable.

## Opciones consideradas

1. `python:3.13` — base Debian completa con todo el tooling (~900 MB).
2. `python:3.13-slim` — Debian mínima (~150 MB), sin compiladores.
3. `python:3.13-alpine` — basada en musl (~50 MB), pero las dependencias
   transitivas de yfinance (`curl_cffi`, `lxml`, wheels de `pandas`)
   exigen `build-base`, headers de `libffi` y `openssl`, y un build
   mucho más largo.
4. `gcr.io/distroless/python3-debian12` — sin shell, sin gestor de
   paquetes (~100 MB). Óptimo para producción pero bloquea
   `podman exec` para debug.

## Decisión

Opción 2 (`python:3.13-slim`) con lo siguiente:

- `PYTHONDONTWRITEBYTECODE=1` y `PYTHONUNBUFFERED=1` para que los logs
  salgan en vivo y no quede `__pycache__` dentro de la imagen.
- `PIP_NO_CACHE_DIR=1` y `PIP_DISABLE_PIP_VERSION_CHECK=1` para
  silenciar el cache de `pip` y el aviso "deberías actualizar pip"
  durante el log del build.
- Un usuario non-root `appuser` (UID 10001) creado con `useradd`. El
  contenedor corre como ese usuario.
- Copia de capas en dos pasos: primero `COPY requirements.txt`, luego
  `pip install`, y al final `COPY app`. Cambios de código no reinstalan
  dependencias.
- Directiva `HEALTHCHECK` apuntando a `/docs` (sin llamada a yfinance,
  sin dependencia de DNS).
- `EXPOSE 8000` como documentación; `CMD ["uvicorn", "app.main:app",
  "--host", "0.0.0.0", "--port", "8000"]`.

## Consecuencias

Bueno:
- Imagen final ~360 MB en v1.1.0, ~459 MB en v1.2.0 (matplotlib + pillow).
- `podman build` y `docker build` son intercambiables (el archivo se
  llama `Containerfile`, no `Dockerfile`, para no implicar que se
  necesita el daemon de Docker).
- Compatible con podman-in-podman, runners de GitHub Actions y pull
  desde `containerd` en el clúster.
- Non-root por default. Encaja con `runAsNonRoot: true` en K8s sin
  conflicto.

Malo / trade-offs:
- Más grande que alpine. Aceptable para una imagen de 459 MB en
  contexto académico.
- El `HEALTHCHECK` en formato OCI se ignora con un warning. Compose y
  K8s lo redefinen donde importa.
