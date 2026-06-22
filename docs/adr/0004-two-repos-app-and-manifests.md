# 0004 — Two repos: app and manifests

- Status: Accepted
- Date: 2026-06-22
- Context: How to separate application code from Kubernetes manifests.

## Context and Problem Statement

The workshop's tagline is "GitOps on Kubernetes". In a GitOps setup, the
cluster syncs configuration from a repository, and the application code lives
somewhere else. A single repo that contains both has worked historically but
mixes two audiences with different permissions and lifecycles.

## Considered Options

1. Single repo with a `deploy/` directory (or `k8s/` directory). One
   audience. Easy to find. Common in small projects.
2. Two repos:
   - `MAS26-grupo4/stockanalyzer-gitops` — application code + Containerfile.
   - `MAS26-grupo4/stockanalyzer-gitops-manifests` — YAML manifests.
3. Repo dedicated to the GitOps tool (Argo CD / Flux) that pulls from
   the previous two.

## Decision

Option 2. Two repos under the same GitHub organization.

The application repo has a `dev` branch used during development and a
`main` branch that triggers CI/CD (see ADR 0009). The manifests repo has
only `main` — the cluster reads from it.

## Consequences

Good:
- Argo CD / Flux (when introduced in a later step) reads from the
  manifests repo; CI/CD pushes the image from the app repo. Clear separation
  of concerns.
- Cluster admin can grant write access on the manifests repo to fewer
  people than the app repo.
- Reproducing a deployment only needs the manifests repo plus the image
  registry; the app repo is not required at runtime.

Bad / trade-offs:
- Two PRs to ship a change (one for the app, one for the manifest that
  bumps the image tag). For a workshop this is fine; for high-velocity
  teams it can be automated with tools like `updatecli` or kept as a
  single PR via monorepo.
- It is now possible to have the cluster pointing to an image that has
  not been pushed yet. Migrations need to be ordered.

Rejected option 3 because Argo CD's "app of apps" pattern is the
standard way to compose multiple sources, and it does not require a third
repo.
