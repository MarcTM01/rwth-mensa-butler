from typing import TYPE_CHECKING

import boto3
from config import config

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table


def __assume_aws_role() -> dict:
    sts_client = boto3.client('sts')
    assumed_role_object = sts_client.assume_role(
        RoleArn=config.dynamodb_config.assume_role_arn,
        RoleSessionName=config.dynamodb_config.assume_role_session_name,
    )
    credentials = assumed_role_object['Credentials']
    return credentials


def get_dynamodb_table() -> 'Table':
    """Obtain the DynamoDB table object for the MensaOfferingsTable."""
    credentials = __assume_aws_role()

    dynamodb = boto3.resource('dynamodb',
                              aws_access_key_id=credentials['AccessKeyId'],
                              aws_secret_access_key=credentials['SecretAccessKey'],
                              aws_session_token=credentials['SessionToken'],
                              region_name=config.dynamodb_config.region)

    table = dynamodb.Table(config.dynamodb_config.table_name)
    return table
