# * INFO: I modified this file and the template.yaml from the following resources:
# * INFO: https://www.tecracer.com/blog/2024/03/adding-basic-authentication-to-the-serverless-dash-app.html
# * INFO: https://github.com/MauriceBrg/aws-blog.de-projects/tree/master/sam-dash-basicauth
"""
Module to add basic auth to a dash app with different credential sources.
"""

import base64
import json
import os

from functools import lru_cache
from typing import Callable, Any

import boto3

ENV_CREDENTIAL_PROVIDER_NAME = "CREDENTIAL_PROVIDER_NAME" # HARDCODED | SSM | SECRETS_MANAGER
ENV_SSM_CREDENTIAL_PARAMETER_NAME = "SSM_CREDENTIAL_PARAMETER_NAME"
ENV_SECRETSMANAGER_CREDENTIAL_SECRET_NAME = "SECRETSMANAGER_CREDENTIAL_SECRET_NAME"
#SECRETSMANAGER_CREDENTIAL_SECRET_NAME = "ytpoppers-api_api-gateway_password"


@lru_cache(maxsize=1)
def get_credentials_from_ssm_parameter() -> dict[str, str]:
    """
    Retrieves the value of the SSM parameter named in the environment variable
    SSM_CREDENTIAL_PARAMETER_NAME, parses it as JSON and returns the resulting
    dictionary.
    """

    ssm_parameter_name = os.environ[ENV_SSM_CREDENTIAL_PARAMETER_NAME]

    get_parameter_response = boto3.client("ssm").get_parameter(
        Name=ssm_parameter_name,
        WithDecryption=True,  # Ignored if not encrypted
    )

    value_as_dict = json.loads(get_parameter_response["Parameter"]["Value"])
    assert isinstance(
        value_as_dict, dict
    ), 'The credentials should be stored as a JSON object, e.g. {"username": "password"}'

    return value_as_dict


@lru_cache(maxsize=1)
def get_credentials_from_secrets_manager() -> dict[str, str]:
    """
    Retrieves the value of the SSM parameter named in the environment variable
    SECRETSMANAGER_CREDENTIAL_SECRET_NAME, parses it as JSON and returns the
    resulting dictionary.
    """

    secret_name = os.environ[ENV_SECRETSMANAGER_CREDENTIAL_SECRET_NAME]
    #secret_name = SECRETSMANAGER_CREDENTIAL_SECRET_NAME

    get_secret_value_response = boto3.client("secretsmanager").get_secret_value(
        SecretId=secret_name
    )

    value_as_dict = json.loads(get_secret_value_response["SecretString"])
    assert isinstance(
        value_as_dict, dict
    ), 'The credentials should be stored as a JSON object, e.g. {"username": "password"}'

    return value_as_dict


CREDENTIAL_PROVIDER_NAME_TO_CREDENTIAL_PROVIDER: dict[
    str, Callable[[], dict[str, str]]
] = {
    # "HARDCODED": lambda: {"avoid": "using_me"},  # You really shouldn't use these.
    "SSM": get_credentials_from_ssm_parameter,
    "SECRETS_MANAGER": get_credentials_from_secrets_manager,
}


class UnauthorizedException(Exception):
    pass


def get_username_and_password_from_header(event: dict[str, Any]) -> tuple[str, str]:
    auth_header = event["authorizationToken"]

    if not auth_header.lower().startswith("basic "):
        raise UnauthorizedException()

    b64_decoded = base64.b64decode(auth_header.split(" ")[1].encode("utf-8")).decode(
        "utf-8"
    )

    username, *password_components = b64_decoded.split(":")

    # Edge case - colon in password
    password = ":".join(password_components)

    return username, password


def lambda_handler(event, _context):
    CREDENTIAL_PROVIDER_NAME = os.environ.get(ENV_CREDENTIAL_PROVIDER_NAME, "HARDCODED")
    credential_provider = CREDENTIAL_PROVIDER_NAME_TO_CREDENTIAL_PROVIDER.get(CREDENTIAL_PROVIDER_NAME)
    valid_credentials = credential_provider()

    try:
        username, password = get_username_and_password_from_header(event)

        correct_password = valid_credentials.get(username)

        if password == correct_password:
            prefix, stage, *_ = event["methodArn"].split("/")

            all_resources_arn = f"{prefix}/{stage}/*"

            policy = {
                "principalId": username,
                "policyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "execute-api:Invoke",
                            "Effect": "Allow",
                            "Resource": all_resources_arn,
                        }
                    ],
                },
            }
            return policy
        else:
            raise UnauthorizedException("Invalid credentials")

    except UnauthorizedException:
        return {
            "principalId": "unauthorized",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Deny",
                        "Resource": event['methodArn']
                    }
                ]
            }
        }
    except Exception as e:
        print(f"Error in authorization: {e}")
        raise

# def lambda_handler(event, context):
#     token = event['authorizationToken']
#     # You need to parse the token, check its validity (e.g., check the username and password)
#     if token == "Basic emZvZ2c6aHVudGVyMgo=":
#         return {
#             "principalId": "user",
#             "policyDocument": {
#                 "Version": "2012-10-17",
#                 "Statement": [
#                     {
#                         "Action": "execute-api:Invoke",
#                         "Effect": "Allow",
#                         "Resource": event['methodArn']
#                     }
#                 ]
#             }
#         }
#     else:
#         raise Exception('Unauthorized')  # Will trigger the 401