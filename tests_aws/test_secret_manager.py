# -*- coding: utf-8 -*-

import sys
import attr
import pytest
from pytest import raises
from pysecret import AWSSecret

py_ver = "py{}{}".format(sys.version_info.major, sys.version_info.minor)
aws = AWSSecret()


@attr.s
class EnvConfig:
    db_password = attr.ib()


@attr.s
class StageConfigs:
    dev = attr.ib()
    prod = attr.ib()


@attr.s
class Config:
    stages = attr.ib()


def teardown_module(module):
    secret_id_list = [
        "pysecret_test_json_path_and_encryption",
        "pysecret_test_update_mode",
        "pysecret_test_deploy_parameter_obj",
    ]
    secret_id_list = [
        "{}_{}".format(py_ver, secret_id)
        for secret_id in secret_id_list
    ]


def test_json_path_and_encryption():
    # deploy secret to AWS
    secret_id = "{}_pysecret_test_json_path_and_encryption".format(py_ver)
    secret_data = dict(
        host="www.example.com",
        port=1234,
        database="mydatabase",
        username="admin",
        password="mypassword",
        metadata=dict(
            creator="Alice",
        )
    )
    res = aws.deploy_secret(
        name=secret_id,
        secret_data=secret_data,
        update_mode=AWSSecret.UpdateModeEnum.try_create,
    )

    # read secret from AWS
    assert aws.get_secret_value(secret_id, "password") == secret_data["password"]
    assert aws.get_secret_value(secret_id, "metadata.creator") == secret_data["metadata"]["creator"]


def test_update_mode():
    secret_id = "{}_pysecret_test_update_mode".format(py_ver)
    secret_data = {"name": "Alice"}
    aws.deploy_secret(
        name=secret_id,
        secret_data=secret_data,
        update_mode=AWSSecret.UpdateModeEnum.try_create,
    )

    with raises(Exception):
        aws.deploy_secret(
            name=secret_id,
            secret_data=secret_data,
            update_mode=AWSSecret.UpdateModeEnum.create,
        )

    secret_data = {"name": "Bob"}
    aws.deploy_secret(
        name=secret_id,
        secret_data=secret_data,
        update_mode=AWSSecret.UpdateModeEnum.upsert,
    )
    assert aws.get_secret_value(secret_id, "name") == "Bob"

    secret_data = {"name": "Cathy"}
    aws.deploy_secret(
        name=secret_id,
        secret_data=secret_data,
        update_mode=AWSSecret.UpdateModeEnum.try_create,
    )
    assert aws.get_secret_value(secret_id, "name") == "Bob"


def test_deploy_secret_obj():
    secret_id = "{}_pysecret_test_deploy_secret_obj".format(py_ver)

    config = Config(
        stages=StageConfigs(
            dev=EnvConfig(db_password="dev_pwd"),
            prod=EnvConfig(db_password="prod_pwd"),
        )
    )
    aws.deploy_secret_object(
        name=secret_id,
        secret_obj=config,
        update_mode=AWSSecret.UpdateModeEnum.try_create,
    )

    obj = aws.get_secret_object(secret_id=secret_id)
    assert isinstance(obj, Config)
    assert isinstance(obj.stages, StageConfigs)
    assert isinstance(obj.stages.dev, EnvConfig)

    assert obj.stages.dev.db_password == "dev_pwd"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
