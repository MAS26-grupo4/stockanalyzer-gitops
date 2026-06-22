# 0010 — Auth via classic PAT in CI/CD (not GITHUB_TOKEN)

- Status: Accepted
- Date: 2026-06-22
- Context: GITHUB_TOKEN had no `write:packages` scope on this org.

## Context and Problem Statement

GitHub Actions on a free organization plan does not always give the
auto-generated `GITHUB_TOKEN` enough scope to push container images to
ghcr.io. The error we saw was:

```
denied: permission_denied: write_package
```

Even after enabling the relevant toggles in the org and repo settings,
the error persisted for our org. We needed a workable alternative for the
workshop.

## Considered Options

1. Continue troubleshooting org-level permissions. Real solution, but
   out of scope for the workshop and dependent on org admin access.
2. Use a fine-grained personal access token. Cleaner but GitHub's
   fine-grained tokens do not surface `Packages: Read and Write` on free
   accounts; that is a paid-org feature.
3. Use a classic personal access token with `read:packages` and
   `write:packages`. Works on any account. The token is stored as a
   repository secret.

## Decision

Option 3. A classic PAT owned by `amcorrea0` with exactly the two
required scopes (`read:packages`, `write:packages`), 90-day expiry,
stored as a repository secret named `CR_PAT` in
`MAS26-grupo4/stockanalyzer-gitops`. The workflow references it as
`${{ secrets.CR_PAT }}` in the `docker/login-action` step.

## Consequences

Good:
- The workshop can demonstrate an end-to-end CI/CD pipeline without
  waiting for org-level policy changes.
- The PAT is scoped to packages only; it cannot read or modify code.

Bad / trade-offs:
- A personal PAT is a shared secret. If `amcorrea0`'s account is
  compromised, the attacker can push images. The blast radius is
  intentionally limited to package push only.
- The PAT must be rotated (manually) every 90 days. We should set a
  calendar reminder or migrate to a fine-grained token once the
  organization has a paid plan.
- The `.env` file accidentally committed during the workshop
  (caught by GitHub push protection) exposed the first PAT, which we
  rotated immediately. The new PAT lives only in the GitHub Actions
  secret store and has never been written to disk.

## Future work

When the organization graduates to a paid plan:

1. Issue a fine-grained token owned by a bot account, scoped only to
   the `stockanalyzer-gitops` package and the
   `MAS26-grupo4/stockanalyzer-gitops` repository.
2. Replace `secrets.CR_PAT` references with that token's secret.
3. Revoke the classic PAT.
