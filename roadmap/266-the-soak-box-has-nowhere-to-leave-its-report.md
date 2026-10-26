# 266. The soak box has nowhere to leave its report, so the laptop has to stay up to fetch it

**Open, in progress since 2026-10-26 in the session "item 266". Filed 2026-10-26 (r1093) at Aria's request. Nobody's call — Aria chose Cloudflare R2.**

Depends on: nothing
Landed: slice 1 (`90fd16e`, r1096).

Aria, 2026-10-26, after the first overnight soak was lost when the laptop dropped its IPv6: *"we shouldn't tie the 8 hour soak to this laptop. It should only depend on that server"*.
She chose that the box cancels itself and uploads its report, and asked whether the upload could go somewhere other than Hetzner's storage; asked where, she chose **Cloudflare R2**, on the account the website already uses, over a private GitHub repository.

## What to build, in botropolis.city

1. **A bucket for soak reports**, `infra/soak.tf`, beside `media.tf` and `packages.tf`: private, no custom domain, and a lifecycle rule that deletes objects after 30 days, since a report is fetched into `~/.local/state/botropolis-perf` and the bucket is only a hand-off.
2. **A credential scoped to that bucket**, object write only, which item 245's runner hands to the soak box. If the Terraform provider's token can create API tokens, create it in Terraform with an expiry and put it in an output marked sensitive; otherwise say so, and Aria creates it by hand in the dashboard, and it goes in 1Password, in the Botropolis vault. Either way the runner reaches it only by a `secret-run` reference, and nothing names the vault or item in a public file beyond the reference shape the Makefile already uses.
3. A way for the laptop to read the reports back: a second, read-only credential, or the existing deploy token if it already reaches R2 objects.

`infra/` applies on push to main, so run the plan first and show the manager what it would create, and push only a plan that creates the bucket and token and touches nothing else.

## What it unblocks

Item 245's slice 3 changes with it: the soak runs detached, the box uploads its report to this bucket as it grows and at the end, and the box is booked at order time to cancel itself, so the laptop is needed only to order and, later, to read the bucket.

## Answered while building

- **How the two keys are made** (Aria, 2026-10-26, asked by the manager): the infra token cannot create API tokens (Cloudflare 403, code 9109), so Aria adds *Account API Tokens: Edit* to it, accepting that it can then mint account tokens, and Terraform makes both keys, each one permission group scoped to the bucket alone and expiring a year out. Aria runs `make soak-credentials` once after the apply. Nothing public names the 1Password items they go in; their names come from the git-ignored `.env`.

## Noticed while building

- **The packages bucket has drifted** (2026-10-26): every plan for this item reported *Drift detected (update)* on `cloudflare_r2_bucket.packages` and `cloudflare_r2_custom_domain.packages` at refresh,
  though none planned a change.
  Nobody has yet looked at what differs from the configuration.
