# 0005 — K8s manifests: minimal viable, no Helm

- Status: Accepted
- Date: 2026-06-22
- Context: First set of Kubernetes manifests for the app.

## Context and Problem Statement

The workshop plan calls for deploying on Kubernetes without Helm first, so
the team can read the actual YAML the cluster receives. We needed to decide
what to include in the first version of the manifests.

## Considered Options

1. Minimal viable: `Namespace`, `Deployment` (2 replicas), `Service`
   (`ClusterIP`), `HorizontalPodAutoscaler` (CPU 70%, 2–5 replicas).
2. Same plus `Strategy: RollingUpdate` with `maxUnavailable: 0`,
   `SecurityContext` (non-root, capabilities), `livenessProbe`,
   `readinessProbe`, `resources.requests/limits`, and a `kustomization.yaml`
   with common labels.
3. Same plus `Ingress` (assumes an ingress controller is installed).

## Decision

Option 1. Four files in `stockanalyzer-gitops-manifests/`:

```
namespace.yaml
deployment.yaml
service.yaml
hpa.yaml
```

The Deployment uses an `app: stockanalyzer` selector (no semantic labels
yet) and pins the image to `ghcr.io/mas26-grupo4/stockanalyzer-gitops:v1.1.0`.

## Consequences

Good:
- Easy to read and explain during the workshop. Nothing is hidden behind
  templating.
- `kubectl apply -f namespace.yaml,deployment.yaml,service.yaml,hpa.yaml`
  works without any tooling.
- Each piece can be justified in isolation. When we add probes in a later
  step, we discuss the *reason* (HEALTHCHECK in OCI is ignored by the
  runtime), not the syntax.

Bad / trade-offs:
- No rolling-update strategy. The default is `25% / 25%` which is fine for
  a stateless API.
- No `runAsNonRoot` enforcement at the cluster level. The `Containerfile`
  ships as `appuser` (UID 10001) which is good enough for the workshop.
- We will need to revisit and add probes, resources, and an HPA stabilization
  window before going to production. They were added incrementally
  (see git history: `resources.requests` after the HPA complained,
  `scaleDown.stabilizationWindowSeconds: 60` after the first scale-down
  took 5 minutes by default).

Rejected option 3 because Ingress depends on a controller that the workshop
cluster does not yet have.
