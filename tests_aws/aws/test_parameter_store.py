# -*- coding: utf-8 -*-

import pytest
import dataclasses

from pysecret.tests import bsm, py_ver, run_cov_test
from pysecret.aws.parameter_store import (
    ParameterTypeEnum,
    Parameter,
    deploy_parameter,
    delete_parameter,
)


def delete_all():
    for name in [
        TestParameter.param_name_string,
        TestParameter.param_name_string_list,
        TestParameter.param_name_secure_string,
        TestParameter.param_name_json_list,
        TestParameter.param_name_json_dict,
        TestParameter.param_name_object,
    ]:
        delete_parameter(bsm.ssm_client, name)


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

    def test_string(self):
        flag = delete_parameter(bsm.ssm_client, self.param_name_string)
        assert flag is False

        param = Parameter.load(bsm.ssm_client, self.param_name_string)
        assert param is None

        # use default kms key but type is not secure string
        with pytest.raises(ValueError):
            deploy_parameter(
                bsm.ssm_client,
                name=self.param_name_string,
                data=STRING,
                type_is_string=True,
                tier_is_standard=True,
                use_default_kms_key=True,
            )

        # use custom kms key but type is not secure string
        with pytest.raises(ValueError):
            deploy_parameter(
                bsm.ssm_client,
                name=self.param_name_string,
                data=STRING,
                type_is_string=True,
                tier_is_standard=True,
                kms_key_id="my-key",
            )

        # type is secure string but no kms key and not use default kms key
        param = deploy_parameter(
            bsm.ssm_client,
            name=self.param_name_string,
            data=STRING,
            description="a string parameter",
            type_is_secure_string=True,
            tier_is_standard=True,
            tags=dict(EnvName="prod"),
        )
        assert param.Value == STRING
        assert param.string == STRING

        param = Parameter.load(bsm.ssm_client, name=self.param_name_string)
        assert param.Value == STRING

        # test aws_account_id and aws_region
        assert len(param.aws_account_id) == 12 and param.aws_account_id[0].isdigit()
        assert param.aws_region == "us-east-1"

    def test_string_list(self):
        param = deploy_parameter(
            bsm.ssm_client,
            name=self.param_name_string_list,
            data=STRING_LIST,
            type_is_string_list=True,
            tier_is_standard=True,
        )
        assert param.string_list == STRING_LIST

        param = Parameter.load(
            bsm.ssm_client,
            name=self.param_name_string_list,
        )
        assert param.Value == ",".join(STRING_LIST)
        assert param.string_list == STRING_LIST

        # string list item doesn't support list of dict
        with pytest.raises(TypeError):
            deploy_parameter(
                bsm.ssm_client,
                name=self.param_name_string_list,
                data=LIST1,
                type_is_string_list=True,
                tier_is_standard=True,
                overwrite=True,
            )

        # string list item cannot have ","
        with pytest.raises(ValueError):
            deploy_parameter(
                bsm.ssm_client,
                name=self.param_name_string_list,
                data=LIST2,
                type_is_string_list=True,
                tier_is_standard=True,
                overwrite=True,
            )

    def test_json_list(self):
        param = deploy_parameter(
            bsm.ssm_client,
            name=self.param_name_json_list,
            data=LIST2,
            type_is_string=True,
            tier_is_advanced=True,
            overwrite=True,
        )
        assert param.json_list == LIST2

        param = Parameter.load(bsm.ssm_client, self.param_name_json_list)
        assert param.json_list == LIST2

    def test_json_dict(self):
        param = deploy_parameter(
            bsm.ssm_client,
            name=self.param_name_json_dict,
            data=DATA,
            type_is_string=True,
            tier_is_intelligent=True,
            overwrite=True,
        )
        assert param.json_dict == DATA

        param = Parameter.load(bsm.ssm_client, self.param_name_json_dict)
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
            bsm.ssm_client,
            name=self.param_name_object,
            data=config,
            type_is_string=True,
            tier_is_intelligent=True,
            overwrite=True,
        )
        py_object = param.py_object
        assert dataclasses.asdict(py_object) == dataclasses.asdict(config)

        param = Parameter.load(bsm.ssm_client, self.param_name_object)
        assert dataclasses.asdict(param.py_object) == dataclasses.asdict(config)


    def test_load_auto_with_encryption(self):
        param = deploy_parameter(
            bsm.ssm_client,
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
            bsm.ssm_client,
            name=self.param_name_secure_string,
            with_decryption=True,
        )
        assert param.json_dict == {"name": "Alice"}

        param = Parameter.load(
            bsm.ssm_client,
            self.param_name_secure_string,
        )
        assert param.json_dict == {"name": "Alice"}

    def test_deploy_parameter_skip_duplicate(self):
        # first deployment
        param = deploy_parameter(
            bsm.ssm_client,
            name=self.param_name_string,
            data=DATA,
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
        )
        _version = param.Version

        param = Parameter.load(bsm.ssm_client, self.param_name_string)
        version = param.Version # store the first deployment version
        assert version == _version

        # second deployment, since the data is not changed, no deployment happen
        param = deploy_parameter(
            bsm.ssm_client,
            name=self.param_name_string,
            data=DATA,
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
            skip_if_duplicated=True,
        )
        assert param is None

        param = Parameter.load(bsm.ssm_client, self.param_name_string)
        assert param.Version == version

        # third deployment, we set skip_if_duplicated = False, so version + 1
        param = deploy_parameter(
            bsm.ssm_client,
            name=self.param_name_string,
            data=DATA,
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
            skip_if_duplicated=False,
        )
        assert param.Version == version + 1

        param = Parameter.load(bsm.ssm_client, self.param_name_string)
        assert param.Version == version + 1

        # fourth deployment, since the data is changed, so version + 1
        param = deploy_parameter(
            bsm.ssm_client,
            name=self.param_name_string,
            data={"key": "a new value"},
            type_is_secure_string=True,
            tier_is_standard=True,
            overwrite=True,
            skip_if_duplicated=True,
        )
        assert param.Version == version + 2

        param = Parameter.load(bsm.ssm_client, self.param_name_string)
        assert param.Version == version + 2

    def test_invalid_args(self):
        with pytest.raises(ValueError):
            deploy_parameter(
                bsm.ssm_client,
                name=self.param_name_string,
                data=DATA,
                kms_key_id="my-key",
                use_default_kms_key=True,
                type_is_secure_string=True,
                tier_is_standard=True,
            )

if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.aws.parameter_store", preview=False)
