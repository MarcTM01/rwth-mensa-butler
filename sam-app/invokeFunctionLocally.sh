#!/usr/bin/env bash
set -euxo pipefail
echo "Starting local dynamodb instance"
docker compose down -v
docker compose up -d

echo "Creating table MensaOfferings"
AWS_ACCESS_KEY_ID=something AWS_SECRET_ACCESS_KEY=different AWS_DEFAULT_REGION=localhost aws dynamodb create-table \
  --table-name MensaOfferings \
  --attribute-definitions \
      AttributeName=MensaIdLanguageKeyDate,AttributeType=S \
  --key-schema \
      AttributeName=MensaIdLanguageKeyDate,KeyType=HASH \
  --billing-mode PROVISIONED \
  --provisioned-throughput \
      ReadCapacityUnits=10,WriteCapacityUnits=10 \
  --endpoint-url=http://localhost:8000

echo "Building SAM application"
sam build

echo "Invoking function locally"
sam local invoke --add-host host.docker.internal:host-gateway --parameter-overrides "ENVIRONMENTNAME=localdev"
