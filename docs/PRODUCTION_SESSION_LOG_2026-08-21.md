# PRODUCTION_SESSION_LOG — 2026-08-21

End-to-end session log for the AfriGround production deployment: from the reported
hydration error to a live, credential-hygiene-clean, fully verified production stack.
Companion doc to `aws_deployment_plan.md` (infra provisioning) and
`CURRENT_FUNCTIONALITY.md` (API surface).

## 1. Session goals

1. Fix the React hydration error #418 reported on the deployed site.
2. Remove every hardcoded key/secret from the repository (including AWS) and move all
   credentials into environment variables.
3. Make the Phase 1–4 backend work *visible* on the client-side website (live feeds).
4. Harden the runtime secrets (rotate the demo JWT secret).

## 2. What was done

### 2.1 Hydration error #418 — FIXED, DEPLOYED, VERIFIED

**Root cause**
`PassSimulatorWidget.tsx:181` formatted a fixed mock pass time (`2026-08-14T18:42:15Z`)
with `toLocaleTimeString([], …)` and no timezone. Vercel's build/runtime is **UTC**, so the
server rendered `06:42:15 PM`; the user's browser is **UTC+8** and rendered `02:42:15 AM`.
The text-node mismatch between server HTML and client hydration triggered #418.

Local testing missed it because the dev machine is also UTC+8 (server and browser agreed).

**Fix (commit `e93b653`)**
All date/time renders now force `timeZone: "UTC"`:

| File | Change |
| --- | --- |
| `apps/web/src/components/PassSimulatorWidget.tsx:181` | `toLocaleTimeString([], { timeZone: "UTC", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false })` |
| `apps/web/src/app/[locale]/data/page.tsx:140` | `toLocaleString([], { timeZone: "UTC" })` |
| `apps/web/src/app/[locale]/station/page.tsx:171,231` | same UTC class (were labeled "UTC" but rendered local time) |
| `apps/web/src/app/[locale]/booking/page.tsx:488-492` | same UTC class |

**Reproduction & verification tooling** (kept in `%TEMP%\opencode\hydration-probe\`)
- Playwright 1.62.1 + chromium used to reproduce: dev server started with `TZ=UTC`
  (mimics Vercel) + browser `timezoneId: "Asia/Shanghai"` (mimics the user) → exact #418
  reproduced before the fix, clean after.
- Production HTML verified via SSM: serves `18:42:15 UTC`.

**Deployments**
- `dpl_JByPbvxGrV8D3ZLu7raoqBC1R69N` (initial fix) → alias `afriground.vercel.app`
- Later superseded by the rotated-secret deployment (see §2.4).

### 2.2 Secrets hygiene — all credentials moved to environment variables

No hardcoded keys remain in the repository. Verified with ripgrep over the tree
(`mockjwtsecret`, `supersecretkey`, dev passwords, AWS key prefixes → zero matches).

**Repository changes (commit `efdafea`)**
- `docker-compose.yml`: every credential via `${VAR:?}` (fails loudly when unset), values
  live in the gitignored root `.env`; `DATABASE_URL`/`AFRIGROUND_WORKER_URL` interpolate
  `${POSTGRES_USER}:${POSTGRES_PASSWORD}`; `mc alias set` uses env values.
- `.env` (repo root, gitignored): holds all local dev secret values.
- `.env.example`: documented env surface, placeholder values only.
- New `apps/api/scripts/_env.py`: shared loader — loads repo-root `.env` when present
  (safe in containers via try/except), `database_url(...)` helper with a passwordless
  localhost fallback.
- `apps/api/scripts/{seed_phase1,outbox_worker,simulate_edge,agent_sim}.py` → read DB URL
  from env via `database_url(...)`.
- `apps/api/tasks.py`, `apps/api/config.py`, `apps/api/tests/conftest.py`: env-driven DB
  URLs, passwordless fallbacks.
- Deleted local `terraform/free/terraform.tfvars` (real secrets; values preserved in SSM).
- `docs/aws_deployment_plan.md`: added `TF_VAR_*` workflow + "Secrets hygiene" section.
- `.gitignore` covers `.env*`, `**/terraform.tfvars`, terraform state/plans, `terraform/free/.ssh/`.

**AWS credentials (CLI-level)**
- Were in `~/.aws/credentials`; moved to **User-level environment variables**
  (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION=ap-northeast-1`).
- `~/.aws/credentials` deleted; `aws sts get-caller-identity` still resolves to
  `arn:aws:iam::005466606114:user/afriground-deploy`.
- The AWS CLI lives at `C:\Users\melam\AppData\Local\Programs\Amazon\AWSCLIV2\aws.exe`
  (not on the shell PATH in the current terminal). Helper
  `%TEMP%\opencode\load-aws-env.ps1` loads the User env vars per command.

### 2.3 Demo data enrichment — live feeds now look real

New idempotent script **`apps/api/scripts/seed_demo_rich.py`** (commits `7ae499e`,
`d6d3fe8`). Run inside the API container (see §3 runbook). Adds:

| Surface | Before | After |
| --- | --- | --- |
| Missions (`/api/v1/missions`) | 1 | **3** (Demo LEO Observation, Atlantic Weather Relay, CropWatch Africa) |
| Satellites | ISS (25544) | + NOAA-19 (33591), SAOCOM-1A (40012), each with TLE set |
| SLA violations (`/api/v1/business/sla-violations`) | 0 | **3** (2 VIOLATED + 1 RESOLVED; unit corrected to `%`) |
| Outbox events (orchestration metrics) | 11 | **17** (all PUBLISHED by the runtime, 0 FAILED → "OUTBOX HEALTHY") |
| Datasets (`/api/v1/data/datasets`) | — | **6** (MULTISPECTRAL/OPTICAL/SAR/HYPERSPECTRAL, L0→L2A products) |
| Ground stations | 1 | **3** (ZADEMO-01 Cape Town, -02 Johannesburg, -03 Durban) with quality scores |
| Network ranking | 1 row | **3 rows** (Cape Town 74.8, Johannesburg 73.2, Durban 72.4) |
| Edge agents (per station) | 0 | ZADEMO-01: 2, ZADEMO-02: 2, ZADEMO-03: 1 |
| Station time-status | 0 | SYNCED/DEGRADED rows on every station |

`_env.py` was hardened to be container-safe (`IndexError` guard when the repo-root `.env`
is absent, e.g. inside the API image).

### 2.4 JWT secret rotation

The demo/service JWT secret (previously `mockjwtsecret`) was rotated to a fresh 64-char
random value. The value is **not** in this repo — it lives in SSM and the runtime envs.

Rollout (order matters so web+API switch together):
1. **SSM** parameter `/afriground/free/supabase_jwt_secret` (SecureString) updated
   (`aws ssm put-parameter --overwrite`, version 2).
2. **Instance** `/opt/afriground/.env` updated via `sed`; API + worker containers
   recreated with
   `docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --no-deps api worker`.
   Healthz verified (`{"status":"ok","db":"up"}`).
3. **Verified**: JWT signed with the new secret → HTTP 200 on `/api/v1/missions`;
   signed with the old secret → HTTP 401.
4. **Vercel**: `SUPABASE_JWT_SECRET` replaced (Sensitive type, Production), web redeployed,
   prod alias re-pointed to the new deployment via
   `POST /v2/deployments/{id}/aliases` (`dpl_FU3AoMzDYnpPrPaCAPyWcarNW4Lk`).
5. **Local dev**: repo-root `.env` and `apps/api/.env` updated to the new value (both
   gitignored).

## 3. Operational runbooks

### Redeploy the web app
```powershell
# from the repo ROOT (Vercel project rootDirectory = apps/web)
vercel --prod
# if the alias is not picked up automatically:
# POST https://api.vercel.com/v2/deployments/<dpl_...>/aliases  body: {"alias":"afriground.vercel.app"}
# token: C:\Users\melam\AppData\Roaming\xdg.data\com.vercel.cli\auth.json
```
Project: `prj_3slLYDuRthSh8zwkG7jH6QUUqukH` · Prod alias: `afriground.vercel.app`.

### Reseed / re-run the demo enrichment
1. Copy the scripts to S3, then onto the instance and into the container:
   ```bash
   aws s3 cp apps/api/scripts/seed_demo_rich.py s3://afriground-free-repo/
   aws s3 cp apps/api/scripts/_env.py s3://afriground-free-repo/
   ```
2. Via SSM (script-file pattern — inline JSON breaks in PowerShell 5.1; use
   `--cli-input-json "file://..."`):
   ```bash
   docker cp /tmp/seed_demo_rich.py afriground-api:/app/scripts/seed_demo_rich.py
   docker cp /tmp/_env.py afriground-api:/app/scripts/_env.py
   docker exec afriground-api python scripts/seed_demo_rich.py
   ```
   The script is idempotent (`get_or_create` by stable keys) and reads `DATABASE_URL` from
   the container env (RDS).

### Rotate a runtime secret (any of the `/afriground/free/*` params)
1. `aws ssm put-parameter --name <param> --value <new> --type SecureString --overwrite`
2. Update the matching key in `/opt/afriground/.env` on the instance.
3. Recreate containers (`docker compose -f docker-compose.yml -f docker-compose.aws.yml
   up -d --no-deps api worker`).
4. If the web app uses it: replace the Vercel env var + redeploy + re-alias.

### SSM one-shot command pattern (host is firewalled; no direct SSH/HTTP from dev machine)
```powershell
$env:AWS_ACCESS_KEY_ID=[Environment]::GetEnvironmentVariable("AWS_ACCESS_KEY_ID","User")
$env:AWS_SECRET_ACCESS_KEY=[Environment]::GetEnvironmentVariable("AWS_SECRET_ACCESS_KEY","User")
$env:AWS_DEFAULT_REGION=[Environment]::GetEnvironmentVariable("AWS_DEFAULT_REGION","User")
aws ssm send-command --cli-input-json "file://<payload.json>" --query Command.CommandId --output text
aws ssm get-command-invocation --command-id <id> --instance-id i-0ba87f670fcf5d059 --query StandardOutputContent --output text
```
- SSM stdout is capped (~24 KB); AWS CLI (Python) fails to encode non-ASCII through the
  console pipe → write `StandardOutputContent` to a file or sanitize on the instance.
- `start-port-forwarding-session` is not supported by the installed CLI version.
- IAM inline policy `afriground-repo-rw` on role `afriground-free-ec2` lets the instance
  upload diagnostics to `s3://afriground-free-repo/`.

## 4. Current live architecture

| Component | Where | State |
| --- | --- | --- |
| Web app | Vercel — `https://afriground.vercel.app` | Deployed, live data, no hydration errors |
| API + Celery worker | EC2 `i-0ba87f670fcf5d059` (t3.micro, AL2023) in Docker | Healthy, `http://13.231.123.242:8000` |
| Postgres/PostGIS | RDS `afriground-free-db…ap-northeast-1` | 60+ tables, alembic head `f1a2b3c4d5e6` |
| Redis | ElastiCache `afriground-free-redis…apne1` | broker/cache |
| Object storage | S3 `afriground-free-repo` (+ MinIO local dev) | diagnostics + dataset staging URLs |
| Secrets | SSM `/afriground/free/*` + Vercel env + `/opt/afriground/.env` | rotated 2026-08-21 |
| AWS identity | IAM user `afriground-deploy` (AdministratorAccess) | keys in User env vars only |

## 5. What the client sees now (hard-refresh to clear the old bundle)

| Page | Live content |
| --- | --- |
| Landing — MISSION CONTROL | `3 ACTIVE` · `OUTBOX HEALTHY` · `3 VIOLATIONS` + alert rows (`AVAILABILITY · target 95% / actual …`) + `LIVE · API FEED` badge |
| Data catalog (`/data`) | 6 datasets from the API (`LIVE · API FEED`), varied sensor/product/cloud-cover |
| Station telemetry (`/station`) | First station (ZADEMO-02) shows 2 agents + 2 time-sync rows; all 3 stations have agents |
| Network ranking | 3 ranked stations with composite scores |
| Support (`/support`) | Tickets persist to RDS |
| Pass simulator / telemetry animation / booking predictions | Simulated by design (offline, no backend dependency) |

## 6. Session commits

```
d6d3fe8  demo: seed edge agents + time status for every station
7ae499e  demo: add seed_demo_rich.py + container-safe _env.py
efdafea  security: move all credentials to environment variables
e93b653  fix(web): render all date/time values in UTC (hydration #418)
d34a605  docs: mark AWS free-tier deployment live (pre-session)
```
All pushed to `origin/main` (`git@github.com:Melakumuka/afriground.git`).

## 7. Known notes / follow-ups

- The `three.js` `THREE.Clock` deprecation warning in the console is benign.
- The IAM deploy user still holds `AdministratorAccess`; scoping it down is a follow-up.
- Real TLE pass predictions for `/booking` (Celestrak) are a proposed follow-up; the
  `SPACETRACK_USERNAME/PASSWORD` env vars already exist.
- SSM stdout size limit and the AWS CLI non-ASCII console-pipe bug are known quirks — see
  §3 runbooks.