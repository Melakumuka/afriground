#!/usr/bin/env bash
# Bootstraps the remote state backend for the AfriGround terraform workspace:
#   - S3 bucket afriground-terraform-state (versioned)
#   - DynamoDB table afriground-terraform-lock (state locking)
# Run once before `terraform init`/`apply`; requires AWS credentials.
set -euo pipefail

REGION="${AWS_REGION:-af-south-1}"
BUCKET="afriground-terraform-state"
TABLE="afriground-terraform-lock"

if ! aws s3api head-bucket --bucket "$BUCKET" --region "$REGION" 2>/dev/null; then
  aws s3api create-bucket \
    --bucket "$BUCKET" \
    --region "$REGION" \
    --create-bucket-configuration LocationConstraint="$REGION" >/dev/null
fi

aws s3api put-bucket-versioning \
  --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled >/dev/null

aws s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true >/dev/null

if ! aws dynamodb describe-table --table-name "$TABLE" --region "$REGION" >/dev/null 2>&1; then
  aws dynamodb create-table \
    --table-name "$TABLE" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "$REGION" >/dev/null
fi

echo "State backend ready: s3://$BUCKET + dynamodb://$TABLE"