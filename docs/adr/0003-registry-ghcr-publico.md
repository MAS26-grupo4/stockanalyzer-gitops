# 0003 — Registry: GitHub Container Registry, paquete público

- Estado: Aceptada
- Fecha: 2026-06-21
- Contexto: Dónde pushear la imagen de contenedor.

## Contexto y problema

La imagen necesita un registry que:
- Sea alcanzable desde podman local durante el desarrollo.
- Sea alcanzable desde un clúster Kubernetes sin que el operador
  gestione `imagePullSecret` adicionales.
- Sea alcanzable desde los runners de GitHub Actions sin malabares con
  credenciales.
- No tenga costo en un contexto académico.

## Opciones consideradas

1. Docker Hub — público, gratis, pero con rate limits molestos
   (anónimo: 100 pulls / 6h). Manejo de namespaces incómodo para
   organizaciones.
2. GitHub Container Registry (`ghcr.io`) — reutiliza la identidad de
   GitHub, soporta PATs classic y `GITHUB_TOKEN` desde Actions, pulls
   ilimitados en paquetes públicos.
3. Quay.io / ECR / GCR — misma idea, más setup, free tiers con letra
   chica.

## Decisión

GitHub Container Registry, paquete
`mas26-grupo4/stockanalyzer-gitops`, visibilidad pública. Pusheamos las
tres primeras versiones manualmente con `podman push` desde la máquina
de desarrollo local, autenticándonos con un PAT classic de GitHub (scopes
`read:packages` y `write:packages`).

La decisión de visibilidad pública queda registrada acá para que
cualquiera que toque el setup del clúster sepa que la imagen no necesita
`imagePullSecret`.

## Consecuencias

Bueno:
- podman local puede hacer `pull` de la misma imagen que usa el
  clúster, sin autenticación.
- `ghcr.io` es el registry default del workflow de GitHub Actions
  (ver ADR 0009), así que la misma historia de auth cubre push y pull.
- Sin sorpresas de rate limit durante el diplomado.

Malo / trade-offs:
- Imágenes públicas implican que cualquiera en internet puede hacer
  pull del binario. Aceptable para un proyecto académico; revisar si la
  app llega a manejar credenciales.
- Un PAT classic se rotó una vez durante el diplomado después de un
  commit accidental de un `.env` (ver ADR 0009).
