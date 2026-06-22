# 0009 — CI/CD con GitHub Actions, docker/build-push-action

- Estado: Aceptada
- Fecha: 2026-06-22
- Contexto: Cómo buildear y pushear la imagen automáticamente en cada
push.

## Contexto y problema

El diplomado tiene un paso de CI/CD. Necesitamos un workflow que:

- Corra en cada push a `main` y en cada tag que matchee `v*.*.*`.
- Buildee la imagen desde el `Containerfile` que ya tenemos.
- Pushee la imagen a `ghcr.io/mas26-grupo4/stockanalyzer-gitops`.
- Taguee la imagen con el semver del tag, o con `dev-<git-sha>` desde
  un push común. Siempre taguea también `latest`.

## Opciones consideradas

1. `buildah` en el runner, llamado directo desde un step de shell.
   Funciona pero requiere `sudo apt-get install -y buildah` y es más
   verboso.
2. `docker/build-push-action` con `setup-buildx-action`. Estándar,
   bien documentado, la elección de facto para `ghcr.io`.
3. Action pre-armada de un tercero que envuelva lo anterior.

## Decisión

Opción 2. Workflow final en
`stockanalyzer-gitops/.github/workflows/build.yml`:

- Triggers: `push` a `main`, y tags que matcheen `v*.*.*`.
- `actions/checkout@v4`.
- Un step de shell que deriva la versión de la imagen (semver desde
  `GITHUB_REF_NAME` si es un tag, si no `dev-${GITHUB_SHA::7}`) y la
  expone como `steps.meta.outputs.version`.
- `docker/setup-buildx-action@v3` y `docker/login-action@v3`.
- `docker/build-push-action@v5` con `file: ./Containerfile` y
  `push: true`, tagueando tanto la versionada como `latest`.

### Dos errores que aparecieron y arreglamos durante el diplomado

1. **`repository name must be lowercase`** — la organización de GitHub
   es `MAS26-grupo4` (con mayúsculas), pero ghcr.io rechaza tags con
   mayúsculas y minúsculas mezcladas. Fix: hardcodear `mas26-grupo4`
   en el env `IMAGE_NAME` del workflow. El repo de manifests ya usa
   `mas26-grupo4`, así que esto queda consistente.
2. **`denied: permission_denied: write_package`** — el `GITHUB_TOKEN`
   por defecto que se emite para Actions en esta organización no tiene
   scope `write:packages`. Después de tocar los toggles relevantes en
   la organización y en el repo, el error persistió, así que caímos a
   un PAT personal (ver ADR 0010).

## Consecuencias

Bueno:
- Cada push a `main` produce un nuevo tag `dev-<sha>` y refresca
  `latest`. El `podman push` manual ya no se necesita para desarrollo.
- Las releases taggeadas (`v*.*.*`) producen imágenes inmutables y
  trazables.
- El workflow vive en el repo de la app, donde corresponde.

Malo / trade-offs:
- Dependemos de un PAT personal guardado como secret del repo (ver
  ADR 0010). Quien posea el token posee la capacidad de pushear al
  paquete.
- El tag `latest` se sobreescribe con cada push a `main`. Si queremos
  un rollout de producción, el manifest debería pinear una versión
  específica, no `latest` (y de hecho lo hace: `v1.1.0` en
  `deployment.yaml`).
