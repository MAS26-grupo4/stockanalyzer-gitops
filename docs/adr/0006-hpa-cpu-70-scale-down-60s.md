# 0006 — HPA: CPU 70% with scaleDown stabilization 60s

- Status: Accepted
- Date: 2026-06-22
- Context: HPA tuning observed during the workshop.

## Context and Problem Statement

The default `HorizontalPodAutoscaler` behavior uses 300 seconds (5 minutes)
for the scale-down stabilization window. During the workshop we observed
the HPA correctly scale from 2 to 5 pods under load, but the descent back
to 2 took the full 5 minutes after the load stopped. That is too long for
a workshop demo.

## Decision

Reduce the scale-down stabilization window to 60 seconds. Keep the default
for scale-up (0 seconds, "be aggressive when more capacity is needed").

The HPA targets CPU at 70% of `requests.cpu` (currently 100m per pod),
and limits replicas to the range 2–5.

## Consequences

Good:
- A scale-down finishes in 60–90 seconds, fast enough to demonstrate the
  full up/down cycle during the workshop.
- The conservative scale-up (0s) still protects against flapping.

Bad / trade-offs:
- A 60-second window can cause oscillation if real traffic is bursty.
  For production, monitor and re-tune.
- We are still using `Resources.requests.cpu: 100m` which is very low. The
  HPA's 70% threshold is therefore only 70m of CPU. Real production should
  size requests based on observed steady-state usage.

## Observed behavior during the workshop

```
23:25:16  cpu: 2%/70%    2 replicas
23:26:32  cpu: 243%/70%  2 replicas    (load starts)
          cpu: 290%/70%  4 replicas    (scaled up)
          cpu: 290%/70%  5 replicas    (reaches maxReplicas)
23:33:43  cpu: 2%/70%    5 replicas
23:34:28  cpu: 2%/70%    2 replicas    (scaled down to min)
```

The HPA events from `kubectl describe hpa` confirm three
`SuccessfulRescale` operations: `New size: 4`, `New size: 5`, `New size: 2`.
