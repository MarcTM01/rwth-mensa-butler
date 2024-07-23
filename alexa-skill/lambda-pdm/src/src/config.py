"""This module defines the data-model for any configuration needed for this app."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DynamoDBConfig(BaseModel):
    """A configuration class for the DynamoDB table connection.

    Attributes:
        table_name:
            The name (identifier) for the DynamoDB table that holds all the data
        region: The region where the DynamoDB table is located
        assume_role_arn: The ARN of a role that has read access to the DynamoDB table
        assume_role_session_name: The session name to use while assuming the ARN
    """

    table_name: str
    region: str
    assume_role_arn: str
    assume_role_session_name: str


class Config(BaseSettings):
    """The main configuration class for the skill.

    Attributes:
        dynamodb_config:
            Configuration required to access the DynamoDB table that stores all the data
    """

    model_config = SettingsConfigDict(
        env_nested_delimiter="__", env_file=".env", env_file_encoding="utf-8"
    )
    dynamodb_config: DynamoDBConfig


config = Config()
