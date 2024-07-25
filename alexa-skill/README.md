# Alexa Skill
This folder contains the source for the Alexa-Hosted Skill which forms the heart of this project.
The skill is written in Python and uses the `ask-sdk` library to interact with the Alexa Skills Kit.

Alexa requires the skill files to follow a strict structure documented [here](https://developer.amazon.com/en-US/docs/alexa/conversations/acdl-understand-directory-structure.html).
Additionally, for Python skills, dependencies must be specified using a `requirements.txt` file.

As a result, several transformations need to take place before the contents of this folder can be uploaded to Alexa.
These include:
- Generating a `requirements.txt` file from the `pdm.lock` file.
- Compiling the `gettext` locale files to `.pot` files.
- Generating a `skill.json` and `.env` file by substituting potentially sensitive values.
- Copying the source files to the correct locations.

The `package.sh` script automates these transformations and packages the skill for upload to Alexa.

## Configuration
The `package.sh` script requires the following environment variables to be set:

For the external DynamoDB table that stores the menu data:
> [!NOTE]
> All the identifiers below are defined outputs of the CloudFormation stack in the `sam-app/` folder of this repository.
- `DYNAMODB_TABLE_NAME` - The name of the DynamoDB table.
- `DYNAMODB_REGION` - The AWS region in which the table is located.
- `DYNAMODB_ASSUME_ROLE_ARN` - The IAM role ARN that the skill can assume to access the table.
- `DYNAMODB_ASSUME_ROLE_SESSION_NAME` - The session name to use when assuming the role.

For the Alexa skill itself:
- `SKILL_LAMBDA_ARN_EUW`, `SKILL_LAMBDA_ARN_USW`, and `SKILL_LAMBDA_ARN_NA` are the skill lambda ARNs found in the
  Alexa developer console.
