# Architecture Decision Records (Registros de Decisiones de Arquitectura)

Este directorio contiene los registros de decisiones de arquitectura
(ADRs) del proyecto `stockanalyzer-gitops`, siguiendo el [template de
Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

Cada ADR captura una decisión significativa: el contexto, las opciones
que consideramos, la elección que tomamos y las consecuencias (buenas y
malas).

## Índice

| # | Título | Estado | Fecha |
|---|---|---|---|
| [0001](0001-estructura-app-router-servicio.md) | Estructura de la app: separación router/servicio | Aceptada | 2026-06-21 |
| [0002](0002-containerfile-python-slim-non-root.md) | Containerfile: python:3.13-slim, usuario non-root | Aceptada | 2026-06-21 |
| [0003](0003-registry-ghcr-publico.md) | Registry: GitHub Container Registry, paquete público | Aceptada | 2026-06-21 |
| [0004](0004-dos-repos-app-y-manifests.md) | Dos repos: app y manifests | Aceptada | 2026-06-22 |
| [0005](0005-manifiestos-k8s-minimo-viable.md) | Manifiestos K8s: mínimo viable, sin Helm | Aceptada | 2026-06-22 |
| [0006](0006-hpa-cpu-70-scaledown-60s.md) | HPA: CPU 70% con scaleDown stabilization 60s | Aceptada | 2026-06-22 |
| [0007](0007-minikube-podman-containerd.md) | Driver de minikube: podman con --container-runtime=containerd | Aceptada | 2026-06-22 |
| [0008](0008-iptables-forward-fix-salida-pods.md) | Reglas iptables FORWARD para tráfico saliente de los pods | Aceptada | 2026-06-22 |
| [0009](0009-ci-cd-github-actions-build-push.md) | CI/CD con GitHub Actions, docker/build-push-action | Aceptada | 2026-06-22 |
| [0010](0010-ci-cd-auth-pat-no-github-token.md) | Auth vía PAT classic en CI/CD (no GITHUB_TOKEN) | Aceptada | 2026-06-22 |

## Qué NO va acá

- **Cambios de código rutinarios** como agregar un endpoint nuevo.
  Esos viven en los mensajes de commit, no en ADRs.
- **Trabajo futuro especulativo.** Documentamos decisiones que se
  tomaron efectivamente, con las alternativas que consideramos y los
  trade-offs que aceptamos.
- **Configuraciones específicas del clúster que viven en el repo de
  manifests.** Para esa parte, ver
  `stockanalyzer-gitops-manifests/README.md`.
