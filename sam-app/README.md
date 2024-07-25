# RWTH Mensa Buttler SAM App

This SAM (Serverless Application Model) App defines all supporting infrastructure required for the skill
besides the AWS-hosted skill itself.

This includes:
1. The DynamoDB table for storing data
2. The Lambda function that scraps the website
3. Triggers that activate the lambda function on a schedule
4. IAM Roles that allow the Scrapping Lambda and the Skill Lambda to communicate with the database

## Requirements

* AWS CLI already configured with Administrator permission
* [Docker installed](https://www.docker.com/community-edition)
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)

## Local development

Local development is focused on the [menu-scrapper-lambda](../menu-scrapper-lambda) project. Please follow the instructions posted there.

## Packaging and deployment

To deploy your application for the first time, run the following in your shell:

```bash
sam deploy --guided
```

