# AfriGround AWS Deployment Plan (Phase 4.3)

> **Deployment status (Aug 2026): the free-tier path is LIVE.** The production
> ECS/ALB plan below remains the "when funded" option; the running deployment
> uses `terraform/free/` (Tokyo, ap-northeast-1) — see "Free-tier deployment
> (live)" at the end of this document.

Status: PLANNED (production path) — execute only with AWS credentials.

## Goal
Take the Phase 4.3 terraform provisioning (already committed) from "code" to
"live": stand up the API + Celery worker on ECS Fargate behind an ALB in
`af-south-1` (Cape Town, African data residency), backed by RDS PostgreSQL 16
and ElastiCache Redis 7, and point the Vercel web app at the public API so the
platform pages serve real data instead of the fail-soft mock fallback.

## What gets provisioned (from terraform/)
| Resource | Detail | Approx monthly cost (april-2026 list, af-south-1) |
|---|---|---|
| VPC | public/private/database subnets, 3 AZs, 1 NAT gateway | ~$32 |
| RDS | `db.r6g.large` Postgres 16, Multi-AZ, 100GB gp3, deletion protection | ~$450 |
| ElastiCache | `cache.t4g.medium` Redis 7, 1 node | ~$130 |
| ECS Fargate | API (512/1024) + worker (512/1024), 1 task each | ~$30 |
| ALB | 1 application LB + target group | ~$16 |
| ECR × 2 | api + worker repos with lifecycle policies | $0 |
| S3 | `afriground-prod-datasets-af-south` (versioned) | storage only |
| SSM | 4–7 SecureString secrets (DB URL, secret keys, optional mTLS certs) | $0.05 per 10k params |
| CloudWatch | 2 log groups, 30-day retention | logs only |

Total baseline ≈ **$650–700/mo**. See "Cost reduction options" before applying.

## Prerequisites
- AWS account with permissions: IAM (roles/policies), VPC, RDS, ElastiCache,
  ECS, ALB, ECR, S3, DynamoDB, SSM, CloudWatch, ECR image push.
- AWS CLI installed + authenticated (access keys or SSO).
- Terraform CLI installed.
- Local docker images `afriground-api:latest` / `afriground-worker:latest`
  (already built in the Phase 4.3 deploy session).

## Steps

### 1. Authenticate
```bash
aws sts get-caller-identity          # confirms who you are + region default
```
Recommended: IAM user with the permissions above + `aws configure`, or
`aws sso login` if the org uses Identity Center.

### 2. Bootstrap remote state (one-time)
State must live in S3 (backend block in `terraform/main.tf`). The committed
`terraform/bootstrap_state.sh` does it; on Windows run the equivalent:
```powershell
aws s3api create-bucket --bucket afriground-terraform-state --region af-south-1 --create-bucket-configuration LocationConstraint=af-south-1
aws s3api put-bucket-versioning --bucket afriground-terraform-state --versioning-configuration Status=Enabled
aws s3api put-public-access-block --bucket afriground-terraform-state --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
aws dynamodb create-table --table-name afriground-terraform-lock --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --billing-mode PAY_PER_REQUEST --region af-south-1
```
Note: bucket name must be globally unique; if `afriground-terraform-state` is
taken, change it in `terraform/main.tf` too.

### 3. Init + plan
No secrets are stored in the repo. Export them as `TF_VAR_*` environment
variables (or keep them in a **gitignored** `terraform/terraform.tfvars`):
```bash
cd terraform
export TF_VAR_db_password='<strong random>'      # or use a secrets manager
export TF_VAR_secret_key='<random 32+ chars>'
export TF_VAR_supabase_url='...'
export TF_VAR_supabase_service_role_key='...'
export TF_VAR_supabase_jwt_secret='...'
terraform init
terraform plan -out=plan.tfplan
```
Review the plan — expect ~35 resources. Confirm no accidental public DB.

### 4. Apply
```bash
terraform apply plan.tfplan
terraform output   # alb_dns_name, rds_endpoint, redis_endpoint, ecr_api_url, ecr_worker_url
```
Give RDS ~10–15 min to reach `available`. Apply the schema migrations:
```powershell
# from a machine with network access to the RDS endpoint (or a bastion/SSM port-forward)
$env:AFRIGROUND_ALEMBIC_URL="postgresql+asyncpg://afriground_admin:<pw>@<rds_endpoint>/afriground"
python -m alembic upgrade head        # from apps/api
```

### 5. Push images to ECR
```powershell
aws ecr get-login-password --region af-south-1 | docker login --username AWS --password-stdin <account_id>.dkr.ecr.af-south-1.amazonaws.com
docker tag afriground-api:latest  <ecr_api_url>:latest
docker tag afriground-worker:latest <ecr_worker_url>:latest
docker push <ecr_api_url>:latest
docker push <ecr_worker_url>:latest
```
Optional tag: `<url>:<git-short>` for rollback pinning. Then force new
deployment (or wait for the services to pick up `latest`):
```powershell
aws ecs update-service --cluster afriground-prod --service afriground-api --force-new-deployment
aws ecs update-service --cluster afriground-prod --service afriground-worker --force-new-deployment
```

### 6. Deploy the web app
Set on Vercel (project `web`, env "Production") — never in the repo:
```
AFRIGROUND_API_URL=http://<alb_dns_name>
AFRIGROUND_SERVICE_SUB=<uuid of the provisioned service user>
AFRIGROUND_SERVICE_ORG=<uuid of that user's organization>
SUPABASE_JWT_SECRET=<same as API>
```
Then `cd apps/web && vercel --prod`.

### 7. Verify
- `curl http://<alb_dns>/health` → 200 `{"status":"ok",...}`
- `curl http://<alb_dns>/api/v1/stations` with a service JWT → real rows
- Web: https://<vercel-app> shows LIVE · API FEED instead of mock fallback
- Worker: CloudWatch `/ecs/afriground-worker` shows `drain_outbox ... succeeded`

## Secrets hygiene
- **AWS credentials**: never commit. Use `~/.aws/credentials` or
  `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` env vars (an IAM user scoped to
  what it needs — the live deployment uses `afriground-deploy`).
- **Local dev**: copy `.env.example` → `.env` (gitignored) and fill values;
  `docker-compose.yml` reads every credential from `.env` via `${VAR:?}`.
- **Terraform**: `TF_VAR_*` env vars (see above) or a gitignored `terraform.tfvars`.
- **AWS runtime**: secrets land in SSM Parameter Store (SecureString) and are
  injected into containers via the ECS task definitions.
- **Vercel**: env vars set in the dashboard per environment.
- **Rotating a leaked secret**: change the value everywhere (SSM + tfvars +
  Vercel) and redeploy; never rewrite git history as the primary defense.

## Cost reduction options (before you burn $700/mo)
- `db.r6g.large` multi-AZ is the dominant cost. For a demo: `db.t4g.small`
  single-AZ (`multi_az=false`, `availability_zone`) ≈ **$40/mo**.
- `cache.t4g.medium` → `cache.t4g.small` ≈ **$60/mo**.
- NAT gateway → `enable_nat_gateway=false` if ECS uses public subnets or SSM
  port-forward instead (saves ~$32).
- Scale ECS desired_count to 0 when idle.

## Rollback / teardown
```bash
terraform plan -destroy -out=destroy.tfplan -var ...   # same vars as apply
terraform apply destroy.tfplan
```
Secrets live in SSM; delete them with the resources. The datasets bucket and
DB snapshots are preserved by default (`skip_final_snapshot=false`).

## Free-tier deployment (live)

The running deployment (verified 2026-08-20) is `terraform/free/` in
`ap-northeast-1` (Tokyo, free-tier eligible; af-south-1 is not):

| Resource | Detail | Cost |
|---|---|---|
| VPC | 2 AZs, no NAT, no ALB | $0 |
| RDS | `db.t3.micro` Postgres 16.14, gp2 20GB, single-AZ | free tier |
| ElastiCache | `cache.t3.micro` Redis 7.1 | free tier |
| EC2 | `t3.micro` AL2023, public IP, runs ONLY api+worker containers | free tier |
| S3 | `afriground-free-repo` (repo zip) + `afriground-free-datasets` | free tier |
| SSM | 4 SecureString params under `/afriground/free/` | ~$0 |

Total ≈ **$0/mo** within the 12-month free tier.

Apply with env-driven vars (no tfvars in the repo):
`TF_VAR_db_password=… TF_VAR_secret_key=… TF_VAR_supabase_jwt_secret=… terraform apply`
(from `terraform/free/`; the secrets then land in SSM `/afriground/free/*`).

- **API:** `http://13.231.123.242:8000` (`.env` on the host written from SSM
  Parameter Store — `/afriground/free/*`; health check `/healthz`; demo service
  JWT is minted by the web app from `SUPABASE_JWT_SECRET` — same value in SSM
  and in the Vercel project env).
- **DB:** `afriground-free-db.<...>.ap-northeast-1.rds.amazonaws.com` — 60 tables,
  alembic at head `f1a2b3c4d5e6`, PostGIS extension created, demo org/user
  seeded with the fixed IDs the web proxy's JWT sub/org expect
  (`b569d5d7-…`, `9b6b697e-…`), admin bound to the `Platform Admin` role.
- **Worker:** celery + beat in the same compose stack; `drain_outbox` runs on
  schedule against RDS + ElastiCache.
- **Management:** SSH (`terraform/free/.ssh/afriground`) + SSM (role carries
  `AmazonSSMManagedInstanceCore`) — the host is managed via `aws ssm
  send-command` since the operator network blocks direct ports.
- **Web:** https://afriground.vercel.app (project `web`, production env:
  `AFRIGROUND_API_URL=http://13.231.123.242:8000`, service sub/org, JWT secret).
  Vercel Authentication was disabled so the domain is public.

### Redeploying the host (bring-up recipe)
1. `git archive HEAD --format=zip -o afriground.zip` (commit first!) and upload
   to `s3://afriground-free-repo/` together with the current `bootstrap.sh`
   (the SSM-driven variant used for the live bring-up).
2. On the instance (or new one): install docker via `dnf`, pin compose
   `v2.24.7` (amazon buildx 0.12.1), unzip, `sed -i 's/\r$//'` over `.sh/.py`
   files (Windows-built archives ship CRLF), write `.env` from SSM, create the
   PostGIS extension with `psql`, then
   `docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d
   --build --no-deps api worker` and `alembic upgrade head`.
3. Seeding is idempotent (`scripts/seed_phase1.py`) but only inserts fixed IDs
   when the org/user are pre-inserted — see the SQL in this bring-up.