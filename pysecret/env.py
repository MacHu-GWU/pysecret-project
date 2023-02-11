# -*- coding: utf-8 -*-

import typing as T
import os
import json
import dataclasses


@dataclasses.dataclass
class BaseEnv:
    """
    A base class for environment secrets data container.
    """

    @classmethod
    def load(cls):
        kwargs = {f.name: os.environ.get(f.name) for f in dataclasses.fields(cls)}
        return cls(**kwargs)

    def to_json(self, pretty: bool=True) -> str:
        kwargs = dict()
        if pretty:
            kwargs["indent"] = 4
        return json.dumps(dataclasses.asdict(self), **kwargs)


@dataclasses.dataclass
class AWSEnvVar(BaseEnv):
    """
    Ref:

    - https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html
    """

    AWS_ACCESS_KEY_ID: T.Optional[str] = dataclasses.field(default=None)
    AWS_CA_BUNDLE: T.Optional[str] = dataclasses.field(default=None)
    AWS_CLI_AUTO_PROMPT: T.Optional[str] = dataclasses.field(default=None)
    AWS_CLI_FILE_ENCODING: T.Optional[str] = dataclasses.field(default=None)
    AWS_CONFIG_FILE: T.Optional[str] = dataclasses.field(default=None)
    AWS_DATA_PATH: T.Optional[str] = dataclasses.field(default=None)
    AWS_DEFAULT_OUTPUT: T.Optional[str] = dataclasses.field(default=None)
    AWS_DEFAULT_REGION: T.Optional[str] = dataclasses.field(default=None)
    AWS_EC2_METADATA_DISABLED: T.Optional[str] = dataclasses.field(default=None)
    AWS_MAX_ATTEMPTS: T.Optional[str] = dataclasses.field(default=None)
    AWS_METADATA_SERVICE_NUM_ATTEMPTS: T.Optional[str] = dataclasses.field(default=None)
    AWS_METADATA_SERVICE_TIMEOUT: T.Optional[str] = dataclasses.field(default=None)
    AWS_PAGER: T.Optional[str] = dataclasses.field(default=None)
    AWS_PROFILE: T.Optional[str] = dataclasses.field(default=None)
    AWS_REGION: T.Optional[str] = dataclasses.field(default=None)
    AWS_RETRY_MODE: T.Optional[str] = dataclasses.field(default=None)
    AWS_ROLE_ARN: T.Optional[str] = dataclasses.field(default=None)
    AWS_ROLE_SESSION_NAME: T.Optional[str] = dataclasses.field(default=None)
    AWS_SECRET_ACCESS_KEY: T.Optional[str] = dataclasses.field(default=None)
    AWS_SESSION_TOKEN: T.Optional[str] = dataclasses.field(default=None)
    AWS_SHARED_CREDENTIALS_FILE: T.Optional[str] = dataclasses.field(default=None)
    AWS_USE_FIPS_ENDPOINT: T.Optional[str] = dataclasses.field(default=None)
    AWS_WEB_IDENTITY_TOKEN_FILE: T.Optional[str] = dataclasses.field(default=None)
