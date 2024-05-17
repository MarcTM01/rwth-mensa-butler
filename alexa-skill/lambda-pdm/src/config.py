from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DynamoDBConfig(BaseModel):
    """A configuration class for the DynamoDB table connection."""
    table_name: str
    region: str
    assume_role_arn: str
    assume_role_session_name: str


class Config(BaseSettings):
    """The main configuration class for the skill."""
    model_config = SettingsConfigDict(env_nested_delimiter='__', env_file='.env', env_file_encoding='utf-8')
    dynamodb_config: DynamoDBConfig


config = Config()
