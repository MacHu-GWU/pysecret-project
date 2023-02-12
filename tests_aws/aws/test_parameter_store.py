# -*- coding: utf-8 -*-

import pytest
import time
import dataclasses

from pysecret.tests import bsm, py_ver, run_cov_test
from pysecret.aws.parameter_store import (
    ParameterTypeEnum,
    Parameter,
    deploy_parameter,
    delete_parameter,
    update_parameter_tags,
)

ssm_client = bsm.ssm_client


def delete_all():
    for name in [
        TestParameter.param_name_string,
        TestParameter.param_name_string_list,
        TestParameter.param_name_secure_string,
        TestParameter.param_name_json_list,
        TestParameter.param_name_json_dict,
        TestParameter.param_name_object,
        TestParameter.param_name_tags,
        TestParameter.param_name_labels,
    ]:
        delete_parameter(ssm_client, name)


def setup_module(module):
    delete_all()


def teardown_module(module):
    delete_all()


STRING = "attach on 4 AM!"
DATA = {"name": "Alice"}
LIST1 = [{"a": 1}, {"b": 2}]
LIST2 = ["hello, alice", "hello, bob"]
STRING_LIST = ["s3://my-bucket", "s3://your-bucket"]


@dataclasses.dataclass
class Env:
    username: str = dataclasses.field()
    password: str = dataclasses.field()


@dataclasses.dataclass
class Config:
    dev: Env = dataclasses.field()
    prod: Env = dataclasses.field()


class TestParameter:
    param_name_string = f"pysecret-{py_ver}-string"
    param_name_string_list = f"pysecret-{py_ver}-string-list"
    param_name_secure_string = f"pysecret-{py_ver}-secure-string"
    param_name_json_list = f"pysecret-{py_ver}-json-list"
    param_name_json_dict = f"pysecret-{py_ver}-json-dict"
    param_name_object = f"pysecret-{py_ver}-object"
    param_name_tags = f"pysecret-{py_ver}-tags"
    param_name_labels = f"pysecret-{py_ver}-labels"

    def test_string(self):
        flag = delete_parameter(ssm_client, self.param_name_string)
        assert flag is False

        param = Parameter.load(ssm_client, self.param_name_string)
        assert param is None

        # use default kms key but type is not secure string
        with pytest.raises(ValueError):
            deploy_parameter(
                ssm_client,
                name=self.param_name_string,
                data=STRING,
                type_is_string=True,
                tier_is_standard=True,
                use_default_kms_key=True,
            )

        # use custom kms key but type is not secure string
        with pytest.raises(ValueError):
            deploy_parameter(
                ssm_client,
                name=self.param_name_string,
                data=STRING,
                type_is_string=True,
                tier_is_standard=True,
                kms_key_id="my-key",
            )

        # type is secure string but no kms key and not use default kms key
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_string,
            data=STRING,
            description="a string parameter",
            type_is_secure_string=True,
            tier_is_standard=True,
            tags=dict(EnvName="prod"),
        )
        assert param.Value == STRING
        assert param.string == STRING

        param = Parameter.load(ssm_client, name=self.param_name_string, with_tags=True)
        assert param.Value == STRING
        assert param.Tags == dict(EnvName="prod")

        # test aws_account_id and aws_region
        assert len(param.aws_account_id) == 12 and param.aws_account_id[0].isdigit()
        assert param.aws_region == "us-east-1"

    def test_string_list(self):
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_string_list,
            data=STRING_LIST,
            type_is_string_list=True,
            tier_is_standard=True,
        )
        assert param.string_list == STRING_LIST

        param = Parameter.load(
            ssm_client,
            name=self.param_name_string_list,
        )
        assert param.Value == ",".join(STRING_LIST)
        assert param.string_list == STRING_LIST

        # string list item doesn't support list of dict
        with pytest.raises(TypeError):
            deploy_parameter(
                ssm_client,
                name=self.param_name_string_list,
                data=LIST1,
                type_is_string_list=True,
                tier_is_standard=True,
                overwrite=True,
            )

        # string list item cannot have ","
        with pytest.raises(ValueError):
            deploy_parameter(
                ssm_client,
                name=self.param_name_string_list,
                data=LIST2,
                type_is_string_list=True,
                tier_is_standard=True,
                overwrite=True,
            )

    def test_json_list(self):
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_json_list,
            data=LIST2,
            type_is_string=True,
            tier_is_advanced=True,
            overwrite=True,
        )
        assert param.json_list == LIST2

        param = Parameter.load(ssm_client, self.param_name_json_list)
        assert param.json_list == LIST2

    def test_json_dict(self):
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_json_dict,
            data=DATA,
            type_is_string=True,
            tier_is_intelligent=True,
            overwrite=True,
        )
        assert param.json_dict == DATA

        param = Parameter.load(ssm_client, self.param_name_json_dict)
        assert param.json_dict == DATA

    def test_object(self):
        config = Config(
            dev=Env(
                username="dev-username",
                password="dev-password",
            ),
            prod=Env(
                username="prod-username",
                password="prod-password",
            ),
        )

        param = deploy_parameter(
            ssm_client,
            name=self.param_name_object,
            data=config,
            type_is_string=True,
            tier_is_intelligent=True,
            overwrite=True,
        )
        py_object = param.py_object
        assert dataclasses.asdict(py_object) == dataclasses.asdict(config)

        param = Parameter.load(ssm_client, self.param_name_object)
        assert dataclasses.asdict(param.py_object) == dataclasses.asdict(config)

    def test_load_auto_with_encryption(self):
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_secure_string,
            data={"name": "Alice"},
            use_default_kms_key=True,
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
            skip_if_duplicated=False,
        )
        assert param.Type == ParameterTypeEnum.secure_string

        param = Parameter.load(
            ssm_client,
            name=self.param_name_secure_string,
            with_decryption=True,
        )
        assert param.json_dict == {"name": "Alice"}

        param = Parameter.load(
            ssm_client,
            self.param_name_secure_string,
        )
        assert param.json_dict == {"name": "Alice"}

    def test_deploy_parameter_skip_duplicate(self):
        # first deployment
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_string,
            data=DATA,
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
        )
        _version = param.Version

        param = Parameter.load(ssm_client, self.param_name_string)
        version = param.Version  # store the first deployment version
        assert version == _version

        # second deployment, since the data is not changed, no deployment happen
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_string,
            data=DATA,
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
            skip_if_duplicated=True,
        )
        assert param is None

        param = Parameter.load(ssm_client, self.param_name_string)
        assert param.Version == version

        # third deployment, we set skip_if_duplicated = False, so version + 1
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_string,
            data=DATA,
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
            skip_if_duplicated=False,
        )
        assert param.Version == version + 1

        param = Parameter.load(ssm_client, self.param_name_string)
        assert param.Version == version + 1

        # fourth deployment, since the data is changed, so version + 1
        param = deploy_parameter(
            ssm_client,
            name=self.param_name_string,
            data={"key": "a new value"},
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
            skip_if_duplicated=True,
        )
        assert param.Version == version + 2

        param = Parameter.load(ssm_client, self.param_name_string)
        assert param.Version == version + 2

    def test_update_tags(self):
        # create without tags
        deploy_parameter(
            ssm_client,
            name=self.param_name_tags,
            data=STRING,
            type_is_string=True,
            tier_is_standard=True,
            overwrite=True,
        )
        param = Parameter.load(ssm_client, self.param_name_tags, with_tags=True)
        assert param.Tags == {}

        # update tags only, without update the parameter
        deploy_parameter(
            ssm_client,
            name=self.param_name_tags,
            data=STRING,
            type_is_string=True,
            tier_is_standard=True,
            tags=dict(ProjectName="pysecret", EnvName="dev"),
            overwrite=True,
        )
        param = Parameter.load(ssm_client, self.param_name_tags, with_tags=True)
        assert param.Tags == dict(ProjectName="pysecret", EnvName="dev")

        # do nothing
        deploy_parameter(
            ssm_client,
            name=self.param_name_tags,
            data=STRING,
            type_is_string=True,
            tier_is_standard=True,
            tags=None,
            overwrite=True,
        )
        param = Parameter.load(ssm_client, self.param_name_tags, with_tags=True)
        assert param.Tags == dict(ProjectName="pysecret", EnvName="dev")

        # update tags is partial update
        update_parameter_tags(
            ssm_client,
            name=self.param_name_tags,
            tags=dict(EnvName="test"),
        )
        param = Parameter.load(ssm_client, self.param_name_tags, with_tags=True)
        assert param.Tags == dict(ProjectName="pysecret", EnvName="test")

        # deploy tags is a full replacement
        deploy_parameter(
            ssm_client,
            name=self.param_name_tags,
            data=STRING,
            type_is_string=True,
            tier_is_standard=True,
            tags=dict(EnvName="prod"),
            overwrite=True,
        )
        param = Parameter.load(ssm_client, self.param_name_tags, with_tags=True)
        assert param.Tags == dict(EnvName="prod")

        # empty dict means remove tag
        deploy_parameter(
            ssm_client,
            name=self.param_name_tags,
            data=STRING,
            type_is_string=True,
            tier_is_standard=True,
            tags={},
            overwrite=True,
        )
        param = Parameter.load(ssm_client, self.param_name_tags, with_tags=True)
        assert param.Tags == {}

    def test_invalid_args(self):
        with pytest.raises(ValueError):
            deploy_parameter(
                ssm_client,
                name=self.param_name_string,
                data=DATA,
                kms_key_id="my-key",
                use_default_kms_key=True,
                type_is_secure_string=True,
                tier_is_standard=True,
            )

    def test_labels(self):
        from rich import print

        param1 = deploy_parameter(
            ssm_client,
            name=self.param_name_labels,
            data="this is version 1",
            type_is_string=True,
            tier_is_standard=True,
            overwrite=True,
        )

        param2 = deploy_parameter(
            ssm_client,
            name=self.param_name_labels,
            data="this is version 2",
            type_is_string=True,
            tier_is_standard=True,
            overwrite=True,
        )

        param1.put_label(
            ssm_client,
            [
                "v0.1.1",
            ],
        )
        param = Parameter.load(ssm_client, self.param_name_labels, label="v0.1.1")
        assert param.Version == 1

        param2.put_label(
            ssm_client,
            [
                "v0.1.1",
            ],
        )
        param = Parameter.load(ssm_client, self.param_name_labels, label="v0.1.1")
        assert param.Version == 2

        time.sleep(6)
        response = param.delete_label(
            ssm_client,
            [
                "v0.1.1",
            ],
        )
        assert response["RemovedLabels"] == [
            "v0.1.1",
        ]

        with pytest.raises(Exception) as e:
            Parameter.load(ssm_client, self.param_name_labels, label="v0.1.1")
        assert "ParameterVersionNotFound" in str(e)


if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.aws.parameter_store", preview=False)
