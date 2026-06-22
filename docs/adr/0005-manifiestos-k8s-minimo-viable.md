# 0005 — Manifiestos K8s: mínimo viable, sin Helm

- Estado: Aceptada
- Fecha: 2026-06-22
- Contexto: Primer set de manifiestos Kubernetes para la app.

## Contexto y problema

El plan del diplomado pide desplegar sobre Kubernetes sin Helm primero,
para que el equipo pueda leer el YAML real que recibe el clúster.
Necesitábamos decidir qué incluir en la primera versión de los
manifiestos.

## Opciones consideradas

1. Mínimo viable: `Namespace`, `Deployment` (2 réplicas), `Service`
   (`ClusterIP`), `HorizontalPodAutoscaler` (CPU 70%, 2–5 réplicas).
2. Igual más `Strategy: RollingUpdate` con `maxUnavailable: 0`,
   `SecurityContext` (non-root, capabilities), `livenessProbe`,
   `readinessProbe`, `resources.requests/limits`, y un
   `kustomization.yaml` con labels comunes.
3. Igual más `Ingress` (asume que hay un ingress controller instalado).

## Decisión

Opción 1. Cuatro archivos en
`stockanalyzer-gitops-manifests/`:

```
namespace.yaml
deployment.yaml
service.yaml
hpa.yaml
```

El Deployment usa un selector `app: stockanalyzer` (todavía sin labels
semánticas) y pinea la imagen a
`ghcr.io/mas26-grupo4/stockanalyzer-gitops:v1.1.0`.

## Consecuencias

Bueno:
- Fácil de leer y explicar durante el diplomado. Nada queda oculto
  detrás de templates.
- `kubectl apply -f namespace.yaml,deployment.yaml,service.yaml,hpa.yaml`
  funciona sin tooling extra.
- Cada pieza se puede justificar aislada. Cuando agreguemos probes en
  un paso posterior, discutimos el *motivo* (el HEALTHCHECK en OCI lo
  ignora el runtime), no la sintaxis.

Malo / trade-offs:
- Sin estrategia de rolling update. El default es `25% / 25%`, que
  está bien para una API stateless.
- Sin enforcement de `runAsNonRoot` a nivel clúster. El `Containerfile`
  ya sale como `appuser` (UID 10001), alcanza para el diplomado.
- Hay que volver y agregar probes, resources y un stabilization window
  para el HPA antes de producción. Se fueron añadiendo incrementalmente
  (ver historial git: `resources.requests` después de que el HPA se
  quejara; `scaleDown.stabilizationWindowSeconds: 60` después de que el
  primer scale-down tardara 5 minutos por default).

Se descartó la opción 3 porque Ingress depende de un controller que el
clúster del diplomado aún no tiene.
