# 0006 — HPA: CPU 70% con scaleDown stabilization 60s

- Estado: Aceptada
- Fecha: 2026-06-22
- Contexto: Tuning del HPA observado durante el diplomado.

## Contexto y problema

El `HorizontalPodAutoscaler` por defecto usa 300 segundos (5 minutos)
como ventana de estabilización para el scale-down. Durante el diplomado
vimos que el HPA escalaba correctamente de 2 a 5 pods bajo carga, pero
el descenso de vuelta a 2 tardaba los 5 minutos completos después de
que la carga paraba. Demasiado para una demo del diplomado.

## Decisión

Reducir la ventana de estabilización del scale-down a 60 segundos.
Mantener el default para scale-up (0 segundos, "ser agresivo cuando se
necesita más capacidad").

El HPA apunta a CPU al 70% de `requests.cpu` (actualmente 100m por pod)
y limita las réplicas al rango 2–5.

## Consecuencias

Bueno:
- Un scale-down termina en 60–90 segundos, suficiente para mostrar el
  ciclo completo arriba/abajo durante el diplomado.
- El scale-up conservador (0s) sigue protegiendo contra flapping.

Malo / trade-offs:
- Una ventana de 60 segundos puede causar oscilación si el tráfico real
  es en ráfagas. Para producción, monitorear y retunear.
- Seguimos con `Resources.requests.cpu: 100m`, que es muy bajo. El
  umbral del 70% del HPA equivale a 70m de CPU. Producción debería
  dimensionar los requests basándose en el uso steady-state observado.

## Comportamiento observado durante el diplomado

```
23:25:16  cpu: 2%/70%    2 réplicas
23:26:32  cpu: 243%/70%  2 réplicas    (empieza la carga)
          cpu: 290%/70%  4 réplicas    (escala arriba)
          cpu: 290%/70%  5 réplicas    (llega a maxReplicas)
23:33:43  cpu: 2%/70%    5 réplicas
23:34:28  cpu: 2%/70%    2 réplicas    (escala abajo al mínimo)
```

Los eventos del HPA en `kubectl describe hpa` confirman tres
`SuccessfulRescale`: `New size: 4`, `New size: 5`, `New size: 2`.
