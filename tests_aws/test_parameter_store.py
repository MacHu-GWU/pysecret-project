# -*- coding: utf-8 -*-

import sys
import json
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
    param_name_list = [
        "pysecret_test_json_path_and_encryption",
        "pysecret_test_update_mode",
        "pysecret_test_deploy_parameter_obj",
    ]
    param_name_list = [
        "{}_{}".format(py_ver, param_name) for param_name in param_name_list
    ]
    aws.ssm_client.delete_parameters(Names=param_name_list)


def test_json_path_and_encryption():
    # deploy parameter to AWS
    param_name = "{}_pysecret_test_json_path_and_encryption".format(py_ver)
    parameter_data = dict(
        project_name="myproject",
        metadata=dict(
            creator="Alice",
        ),
    )
    aws.deploy_parameter(
        name=param_name,
        parameter_data=parameter_data,
        update_mode=AWSSecret.UpdateModeEnum.try_create,
        use_default_kms_key=True,
    )

    # read parameter from AWS
    assert (
        aws.get_parameter_value(param_name, "project_name", with_encryption=True)
        == parameter_data["project_name"]
    )
    assert (
        aws.get_parameter_value(param_name, "metadata.creator", with_encryption=True)
        == parameter_data["metadata"]["creator"]
    )
    json.loads(aws.get_parameter_raw_value(param_name, with_encryption=True))


def test_update_mode():
    param_name = "{}_pysecret_test_update_mode".format(py_ver)
    param_data = {"name": "alice"}
    response = aws.deploy_parameter(
        name=param_name,
        parameter_data=param_data,
        update_mode=AWSSecret.UpdateModeEnum.try_create,
    )
    assert "Version" in response

    with raises(Exception):
        aws.deploy_parameter(
            name=param_name,
            parameter_data=param_data,
            update_mode=AWSSecret.UpdateModeEnum.create,
        )

    param_data = {"name": "Bob"}
    response = aws.deploy_parameter(
        name=param_name,
        parameter_data=param_data,
        update_mode=AWSSecret.UpdateModeEnum.upsert,
    )
    assert "Version" in response
    assert aws.get_parameter_value(param_name, "name") == "Bob"

    response = aws.deploy_parameter(
        name=param_name,
        parameter_data=param_data,
        update_mode=AWSSecret.UpdateModeEnum.upsert,
    )
    assert response == {}

    param_data = {"name": "Cathy"}
    aws.deploy_parameter(
        name=param_name,
        parameter_data=param_data,
        update_mode=AWSSecret.UpdateModeEnum.try_create,
    )
    assert aws.get_parameter_value(param_name, "name") == "Bob"


def test_deploy_parameter_obj():
    param_name = "{}_pysecret_test_deploy_parameter_obj".format(py_ver)

    config = Config(
        stages=StageConfigs(
            dev=EnvConfig(db_password="dev_pwd"),
            prod=EnvConfig(db_password="prod_pwd"),
        )
    )

    response = aws.deploy_parameter_object(
        name=param_name,
        parameter_obj=config,
        update_mode=AWSSecret.UpdateModeEnum.try_create,
    )
    assert "Version" in response

    obj = aws.get_parameter_object(name=param_name)
    assert isinstance(obj, Config)
    assert isinstance(obj.stages, StageConfigs)
    assert isinstance(obj.stages.dev, EnvConfig)

    assert obj.stages.dev.db_password == "dev_pwd"

    jsonpickle_content = aws.get_parameter_raw_value(param_name, with_encryption=True)
    assert "dev_pwd" in jsonpickle_content
    assert "prod_pwd" in jsonpickle_content

    response = aws.deploy_parameter_object(
        name=param_name,
        parameter_obj=config,
        update_mode=AWSSecret.UpdateModeEnum.upsert,
    )
    assert response == {}


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
