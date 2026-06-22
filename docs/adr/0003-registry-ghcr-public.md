# 0003 — Registry: GitHub Container Registry, public package

- Status: Accepted
- Date: 2026-06-21
- Context: Where to push the container image.

## Context and Problem Statement

The image needs a registry that:
- Is reachable from local podman for development.
- Is reachable from a Kubernetes cluster without the operator managing
  custom pull secrets.
- Is reachable from GitHub Actions runners without juggling additional
  credentials.
- Costs nothing in a teaching context.

## Considered Options

1. Docker Hub — public, free, but limited by image pull rate limits
   (anonymous: 100 pulls / 6h). Awkward namespace handling for orgs.
2. GitHub Container Registry (`ghcr.io`) — reuses the GitHub identity,
   supports both classic PATs and `GITHUB_TOKEN` for Actions, unlimited
   pulls on public packages.
3. Quay.io / ECR / GCR — same idea, more setup, free tiers with caveats.

## Decision

GitHub Container Registry, package `mas26-grupo4/stockanalyzer-gitops`,
public visibility. We pushed the first three versions manually with
`podman push` from the local dev machine after authenticating with a
GitHub classic PAT (scopes `read:packages` and `write:packages`).

The public visibility decision is recorded here so that anyone touching the
cluster setup knows the image does not need `imagePullSecret`.

## Consequences

Good:
- Local podman can `pull` the same image the cluster uses, with no auth.
- `ghcr.io` is the default registry for the GitHub Actions workflow (see
  ADR 0009), so the same auth story covers both push and pull.
- No rate-limit surprises during the workshop.

Bad / trade-offs:
- Public images mean anyone on the internet can pull the binary. Acceptable
  for an academic project; revisit if the app ever handles credentials.
- A classic PAT was rotated once during the workshop after an accidental
  commit of a `.env` file (see ADR 0009).
