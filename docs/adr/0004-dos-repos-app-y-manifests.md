# 0004 — Dos repos: app y manifests

- Estado: Aceptada
- Fecha: 2026-06-22
- Contexto: Cómo separar el código de aplicación de los manifiestos de
Kubernetes.

## Contexto y problema

El leitmotiv del diplomado es "GitOps sobre Kubernetes". En un setup
GitOps el clúster sincroniza configuración desde un repositorio, y el
código de la aplicación vive en otro. Un único repo con todo dentro
funciona históricamente pero mezcla dos audiencias con permisos y ciclos
de vida distintos.

## Opciones consideradas

1. Un solo repo con un directorio `deploy/` (o `k8s/`). Una sola
   audiencia. Fácil de encontrar. Común en proyectos chicos.
2. Dos repos:
   - `MAS26-grupo4/stockanalyzer-gitops` — código de la app + Containerfile.
   - `MAS26-grupo4/stockanalyzer-gitops-manifests` — YAML de manifiestos.
3. Repo dedicado a la herramienta GitOps (Argo CD / Flux) que pulla de
   los dos anteriores.

## Decisión

Opción 2. Dos repos bajo la misma organización de GitHub.

El repo de la app tiene una rama `dev` usada durante el desarrollo y una
rama `main` que dispara el CI/CD (ver ADR 0009). El repo de manifests
tiene solo `main` — el clúster lee de ahí.

## Consecuencias

Bueno:
- Argo CD / Flux (cuando los introduzcamos en un paso posterior) lee
  desde el repo de manifests; el CI/CD pushea la imagen desde el repo
  de la app. Separación de responsabilidades clara.
- El admin del clúster puede dar acceso de escritura sobre el repo de
  manifests a menos gente que sobre el repo de la app.
- Reproducir un despliegue solo necesita el repo de manifests más el
  registry de imágenes; el repo de la app no se requiere en runtime.

Malo / trade-offs:
- Dos PRs para llevar un cambio a producción (uno de la app, otro del
  manifest que bumpea el tag). En el diplomado está bien; en equipos
  de alta velocidad se automatiza con herramientas tipo `updatecli` o
  se mantiene como un único PR vía monorepo.
- Ahora es posible que el clúster apunte a una imagen que aún no se
  pusheó. Las migraciones hay que ordenarlas.

Se descartó la opción 3 porque el patrón "app of apps" de Argo CD es la
manera estándar de componer múltiples sources y no necesita un tercer
repo.
