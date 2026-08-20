#!/bin/bash
# AfriGround free-tier host bootstrap (rendered by terraform).
# Installs docker, pulls the repo from S3, writes .env from SSM, creates the
# PostGIS extension, and starts ONLY the api + worker containers against the
# AWS-managed RDS/Redis. Proven steps — mirrored by terraform/free + the
# bootstrap.sh used during the live bring-up (see docs/aws_deployment_plan.md).
set -euxo pipefail

exec > /var/log/afriground-bootstrap.log 2>&1

REGION="${region}"
REPO_BUCKET="${repo_bucket}"
REPO_KEY="${repo_key}"

# ── docker (amazonlinux package; get.docker.com does not support 'amzn') ─────
dnf install -y docker
systemctl enable --now docker
systemctl start docker
sleep 5
# pin compose to a build compatible with the amazon buildx 0.12.1
mkdir -p /usr/local/lib/docker/cli-plugins
curl -sL https://github.com/docker/compose/releases/download/v2.24.7/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# ── repo ─────────────────────────────────────────────────────────────────────
mkdir -p /opt/afriground
aws s3 cp "s3://$${REPO_BUCKET}/$${REPO_KEY}" /tmp/afriground.zip --region "$${REGION}"
unzip -o /tmp/afriground.zip -d /opt/afriground
# normalize line endings (Windows-built archives ship CRLF, breaks entrypoint.sh)
find /opt/afriground -type f \( -name '*.sh' -o -name 'Dockerfile' -o -name '*.py' \
  -o -name '*.ini' -o -name '*.yml' \) -exec sed -i 's/\r$//' {} +

# ── env from SSM ─────────────────────────────────────────────────────────────
DATABASE_URL=$(aws ssm get-parameter --name "${db_url_param}" --with-decryption --query Parameter.Value --output text --region "$${REGION}")
SECRET_KEY=$(aws ssm get-parameter --name "${secret_key_param}" --with-decryption --query Parameter.Value --output text --region "$${REGION}")
SUPABASE_SERVICE_ROLE_KEY=$(aws ssm get-parameter --name "${supabase_role_param}" --with-decryption --query Parameter.Value --output text --region "$${REGION}")
SUPABASE_JWT_SECRET=$(aws ssm get-parameter --name "${supabase_jwt_param}" --with-decryption --query Parameter.Value --output text --region "$${REGION}")

cat > /opt/afriground/.env <<EOF
DATABASE_URL=$${DATABASE_URL}
REDIS_URL=redis://${redis_host}:6379/0
CELERY_BROKER_URL=redis://${redis_host}:6379/0
SECRET_KEY=$${SECRET_KEY}
SUPABASE_URL=${supabase_url}
SUPABASE_SERVICE_ROLE_KEY=$${SUPABASE_SERVICE_ROLE_KEY}
SUPABASE_JWT_SECRET=$${SUPABASE_JWT_SECRET}
API_CORS_ORIGINS=${api_cors}
AFRIGROUND_ORCHESTRATION_SIMULATE=1
EOF

# ── PostGIS extension (models use geometry(POINT,4326)) ──────────────────────
if ! command -v psql >/dev/null; then
  dnf install -y postgresql15
fi
PGURL=$${DATABASE_URL/postgresql+asyncpg:/postgresql:}
psql "$PGURL" -v ON_ERROR_STOP=1 -c "CREATE EXTENSION IF NOT EXISTS postgis;" || \
  echo "POSTGIS CREATE FAILED"

# ── start api + worker (AWS Postgres/Redis, not the compose containers) ──────
cd /opt/afriground
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build --no-deps api worker

# ── migrate ──────────────────────────────────────────────────────────────────
sleep 20
docker compose -f docker-compose.yml -f docker-compose.aws.yml exec -T api python -m alembic upgrade head || \
  echo "ALEMBIC UPGRADE FAILED — check /var/log/afriground-bootstrap.log"

echo "AFRIGROUND BOOTSTRAP COMPLETE"