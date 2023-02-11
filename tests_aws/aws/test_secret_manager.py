# -*- coding: utf-8 -*-

import pytest
import time

from pysecret.tests import bsm, py_ver, run_cov_test
from pysecret.aws.secret_manager import (
    Secret,
    deploy_secret,
    delete_secret,
)
from rich import print as rprint

sm_client = bsm.secretsmanager_client


def delete_all():
    for name in [
        TestSecret.secret_name_bytes,
        TestSecret.secret_name_string,
        TestSecret.secret_name_json_dict,
    ]:
        delete_secret(sm_client, name, force_delete_without_recovery=True)


def setup_module(module):
    delete_all()


def teardown_module(module):
    delete_all()


BINARY = "f7e044fd1b4ca303d479daaf5759f841".encode("utf-8")
STRING = "attach on 4 AM!"
DATA = {"name": "Alice"}


class TestSecret:
    secret_name_bytes = f"pysecret-{py_ver}-bytes"
    secret_name_string = f"pysecret-{py_ver}-string"
    secret_name_json_dict = f"pysecret-{py_ver}-json-dict"

    def test_bytes(self):
        secret = Secret.load(sm_client, self.secret_name_bytes)
        assert secret is None

        secret = deploy_secret(
            sm_client,
            name_or_arn=self.secret_name_bytes,
            data=BINARY,
            description="My first secret",
            skip_if_duplicated=False,
        )
        assert secret.SecretBinary == BINARY
        assert secret.binary == BINARY
        v1 = secret.VersionId

        # test aws_account_id and aws_region
        assert len(secret.aws_account_id) == 12 and secret.aws_account_id[0].isdigit()
        assert secret.aws_region == "us-east-1"

        # test the skip_if_duplicated arg
        # this time no deployment happen
        secret = deploy_secret(
            sm_client,
            name_or_arn=self.secret_name_bytes,
            data=BINARY,
            skip_if_duplicated=True,
        )
        assert secret is None

        secret = Secret.load(sm_client, self.secret_name_bytes)
        assert secret.VersionId == v1

        # this time skip_if_duplicated = False
        secret = deploy_secret(
            sm_client,
            name_or_arn=self.secret_name_bytes,
            data=BINARY,
            skip_if_duplicated=False,
        )
        assert secret is not None
        v2 = secret.VersionId

        secret = Secret.load(sm_client, self.secret_name_bytes)
        assert secret.VersionId != v1
        assert secret.VersionId == v2

        # this time data is changed
        secret = deploy_secret(
            sm_client,
            name_or_arn=self.secret_name_bytes,
            data="a4ebb9d8e4a6470331f1e473e46c1589".encode("utf-8"),
            skip_if_duplicated=True,
        )
        assert secret is not None
        v3 = secret.VersionId

        secret = Secret.load(sm_client, self.secret_name_bytes)
        assert secret.VersionId not in [v1, v2]
        assert secret.VersionId == v3

    def test_string(self):
        secret = Secret.load(sm_client, self.secret_name_string)
        assert secret is None

        secret = deploy_secret(
            sm_client,
            name_or_arn=self.secret_name_string,
            data=STRING,
        )
        assert secret.SecretString == STRING

        secret = Secret.load(sm_client, self.secret_name_string)
        assert secret.SecretString == STRING
        assert secret.string == STRING

    def test_json_dict(self):
        secret = Secret.load(sm_client, self.secret_name_json_dict)
        assert secret is None

        secret = deploy_secret(
            sm_client,
            name_or_arn=self.secret_name_json_dict,
            data=DATA,
            tags=dict(EnvName="dev"),  # with tagging
        )
        assert secret.json_dict == DATA

        secret = Secret.load(sm_client, self.secret_name_json_dict)
        assert secret.json_dict == DATA

        # verify tagging
        response = sm_client.describe_secret(SecretId=self.secret_name_json_dict)
        tags = {dct["Key"]: dct["Value"] for dct in response["Tags"]}
        assert tags == dict(EnvName="dev")

        # deploy new data with new tag
        new_data = {"name": "Bob"}
        secret = deploy_secret(
            sm_client,
            name_or_arn=self.secret_name_json_dict,
            data=new_data,
            tags=dict(EnvName="prod"),
        )
        response = sm_client.describe_secret(SecretId=self.secret_name_json_dict)
        tags = {dct["Key"]: dct["Value"] for dct in response["Tags"]}
        assert tags == dict(EnvName="prod")


def test_delete_secret():
    assert delete_secret(sm_client, name_or_arn="pysecret-never-exists") is False


if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.aws.secret_manager", preview=False)
