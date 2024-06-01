#!/usr/bin/env bash
set -euxo pipefail
echo "Starting local dynamodb instance"
docker compose down -v
docker compose up -d --build --wait

invoke_dynamodb() {
  AWS_ACCESS_KEY_ID=something AWS_SECRET_ACCESS_KEY=different AWS_DEFAULT_REGION=localhost aws dynamodb "$1" \
    --table-name MensaOfferings \
    --endpoint-url=http://localhost:8000 \
    "${@:2}"
}

echo "Creating table MensaOfferings"
invoke_dynamodb create-table \
  --attribute-definitions \
      AttributeName=MensaIdLanguageKeyDate,AttributeType=S \
  --key-schema \
      AttributeName=MensaIdLanguageKeyDate,KeyType=HASH \
  --billing-mode PROVISIONED \
  --provisioned-throughput \
      ReadCapacityUnits=10,WriteCapacityUnits=10

echo "Building SAM application"
sam build

echo "Invoking function locally"
mkdir -p testing_artifacts
sam local invoke --add-host host.docker.internal:host-gateway --parameter-overrides "ENVIRONMENTNAME=localdev" -l testing_artifacts/invocation.log

# Create a database dump
invoke_dynamodb scan > testing_artifacts/database_dump.json

# Check if the log file contains at least one error
if grep -iq "\[ERROR\]" testing_artifacts/invocation.log; then
    echo "The log file contains at least one error!"
    exit 1
else
    echo "The log file does not contain [ERROR]"
fi

# Check if the log file contains the correct number of occurrences of the success message
storage_count=$(grep -c "\[INFO\] Successfully stored 9 days of offerings" testing_artifacts/invocation.log)
expected_storage_count=18

if [ "$storage_count" -ne "$expected_storage_count" ]; then
    echo "Error: The log file contains $storage_count occurrences of '[INFO] Successfully stored 9 days of offerings', but it should be $expected_storage_count."
    exit 1
else
    echo "The log file contains the correct number of occurrences ($expected_storage_count) of '[INFO] Successfully stored 9 days of offerings'."
fi

# Check if the database contains the correct number of items
database_entry_count=$(invoke_dynamodb scan --select "COUNT" | jq -r '.Count')
expected_database_entry_count=162

if [ "$database_entry_count" -ne "$expected_database_entry_count" ]; then
    echo "Error: The database contains $database_entry_count items, but it should be $expected_database_entry_count."
    exit 1
else
    echo "The database contains the correct number of items ($expected_database_entry_count)."
fi

# Check if the database contains at least one correct entry
menu_expected_falafel=$(invoke_dynamodb get-item --key '{"MensaIdLanguageKeyDate": {"S": "mensa-academica;en;2024-05-31"}}' | jq -r '.Item.Menus.L[0].M.Contents.L[0].S')

if [ "$menu_expected_falafel" != "Falafel" ]; then
    echo "Error: The database does not contain the expected entry for mensa-academica;en;2024-05-31."
    exit 1
else
    echo "The database contains the expected entry for mensa-academica;en;2024-05-31."
fi