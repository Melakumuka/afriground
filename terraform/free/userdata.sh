#!/bin/bash
# AfriGround free-tier host bootstrap (rendered by terraform).
# Installs docker, pulls the repo from S3, writes .env from SSM, and starts
# ONLY the api + worker containers against the AWS-managed RDS/Redis.
set -euxo pipefail

exec > /var/log/afriground-bootstrap.log 2>&1

REGION="${region}"
REPO_BUCKET="${repo_bucket}"
REPO_KEY="${repo_key}"

# ── docker ───────────────────────────────────────────────────────────────────
dnf install -y docker docker-compose-plugin
systemctl enable --now docker
usermod -aG docker ec2-user

# ── repo ─────────────────────────────────────────────────────────────────────
mkdir -p /opt/afriground
aws s3 cp "s3://$${REPO_BUCKET}/$${REPO_KEY}" /tmp/afriground.zip --region "$${REGION}"
unzip -o /tmp/afriground.zip -d /opt/afriground

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

# ── start api + worker (AWS Postgres/Redis, not the compose containers) ──────
cd /opt/afriground
docker compose -f docker-compose.yml -f docker-compose.aws.yml up -d --build --no-deps api worker

# ── migrate ──────────────────────────────────────────────────────────────────
sleep 20
docker compose -f docker-compose.yml -f docker-compose.aws.yml exec -T api python -m alembic upgrade head || \
  echo "ALEMBIC UPGRADE FAILED — check /var/log/afriground-bootstrap.log"

echo "AFRIGROUND BOOTSTRAP COMPLETE"