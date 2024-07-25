# Menu Scraper Lambda
An AWS Lambda function written in Go that uses [menu-scraper-lib](../menu-scraper-lib) to scrape the cafeteria menus and store them in an Amazon DynamoDB table.

## Local Development & Testing
You can run this lambda function locally. To do so, check out the [performLocalIntegrationTest.sh](../sam-app/performLocalIntegrationTest.sh).
This script sets up a fully self-contained testing environment including:
1. A local DynamoDB instance to connect to.
2. A web server mimicking the website of the canteens to ensure reproducibility.

The latter step has the added bonus of allowing this script to run frequently in a CI pipeline without causing
additional load on the canteen's websites.

## Code Quality & Testing
- We use `go fmt` for code formatting.
- We use [golangci-lint](https://github.com/golangci/golangci-lint) for linting.
