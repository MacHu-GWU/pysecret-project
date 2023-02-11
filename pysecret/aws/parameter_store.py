# -*- coding: utf-8 -*-

"""
AWS Parameter Store support.
"""

import typing as T
import json
import enum
import dataclasses
from datetime import datetime

try:
    import jsonpickle

    has_jsonpickle = True
except ImportError:  # pragma: no cover
    has_jsonpickle = False

from ..compat import cached_property
from ..js_helper import strip_comments
from ..helper import ensure_only_one_true

JSON_PICKLE_KEY = "__jsonpickle__"


class ParameterTypeEnum(str, enum.Enum):
    string = "String"
    string_list = "StringList"
    secure_string = "SecureString"


DEFAULT_KMS_KEY = "alias/aws/ssm"


class ParameterTierEnum(str, enum.Enum):
    standard = "Standard"
    advanced = "Advanced"
    intelligent_tiering = "Intelligent-Tiering"


class ParameterDataTypeEnum(str, enum.Enum):
    text = "text"
    ec2_image = "aws:ec2:image"


@dataclasses.dataclass
class Parameter:
    """
    AWS System Manager Parameter object.

    - The camel case attributes are raw value from AWS API.
    - The snake case attributes are user-friendly accessor to the data.
    - if you know what data type to expect in the parameter, please use
        :meth:`Parameter.string`, :meth:`Parameter.string_list`,
        :meth:`Parameter.json_dict`, :meth:`Parameter.json_list`,
        :meth:`Parameter.py_object` to access the data.
    """
    Name: str = dataclasses.field()
    Type: str = dataclasses.field()
    Value: str = dataclasses.field()
    Version: int = dataclasses.field()
    LastModifiedDate: datetime = dataclasses.field()
    DataType: str = dataclasses.field()
    ARN: T.Optional[str] = dataclasses.field(default=None)
    Selector: T.Optional[str] = dataclasses.field(default=None)
    SourceResult: T.Optional[str] = dataclasses.field(default=None)

    @classmethod
    def load(
        cls,
        ssm_client,
        name: str,
        with_decryption: T.Optional[bool] = None,
    ) -> T.Optional["Parameter"]:
        """
        Load parameter data.

        Ref:

        - get_parameter: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter
        """
        kwargs = dict(Name=name)
        if with_decryption is not None:
            kwargs["WithDecryption"] = with_decryption

        # get the parameter data
        try:
            response = ssm_client.get_parameter(**kwargs)
            parameter = cls(
                Name=response["Parameter"]["Name"],
                Type=response["Parameter"]["Type"],
                Value=response["Parameter"]["Value"],
                Version=response["Parameter"]["Version"],
                LastModifiedDate=response["Parameter"]["LastModifiedDate"],
                DataType=response["Parameter"]["DataType"],
                ARN=response["Parameter"]["ARN"],
                Selector=response["Parameter"].get("Selector"),
                SourceResult=response["Parameter"].get("SourceResult"),
            )
            # check if the Type is secure string
            if parameter.Type == ParameterTypeEnum.secure_string.value:
                # if already set with_decryption = True, then return
                if with_decryption is True:
                    return parameter
                # if forget to set with_description = True, then do it again
                else:
                    return cls.load(ssm_client, name, True)
            else:
                return parameter
        # if not exists, return None
        except Exception as e:
            if "ParameterNotFound" in str(e):
                return None
            else:  # pragma: no cover
                raise e

    @classmethod
    def _from_put_parameter_response(
        cls,
        put_parameter_kwargs: dict,
        put_parameter_response: dict,
    ):
        return Parameter(
            Name=put_parameter_kwargs["Name"],
            Type=put_parameter_kwargs["Type"],
            Value=put_parameter_kwargs["Value"],
            Version=put_parameter_response["Version"],
            LastModifiedDate=datetime.strptime(
                put_parameter_response["ResponseMetadata"]["HTTPHeaders"]["date"],
                "%a, %d %b %Y %H:%M:%S %Z",
            ),
            ARN=None,
            DataType="text",
        )

    @property
    def string(self) -> str:
        """
        The string user data.
        """
        return self.Value

    @cached_property
    def string_list(self) -> T.List[str]:
        """
        The python string list user data.
        """
        return self.Value.split(",")

    @cached_property
    def json_dict(self) -> dict:
        """
        The python dict user data.
        """
        return json.loads(strip_comments(self.Value))

    @cached_property
    def json_list(self) -> list:
        """
        The python list user data.
        """
        return json.loads(strip_comments(self.Value))

    @cached_property
    def py_object(self):
        if has_jsonpickle is False:  # pragma: no cover
            raise ImportError(
                "you have to install `jsonpickle` to store arbitrary "
                "python object in AWS Parameter Store."
            )
        return jsonpickle.loads(json.loads(self.Value)[JSON_PICKLE_KEY])

    @property
    def aws_account_id(self) -> str:
        return self.ARN.split(":")[4]

    @property
    def aws_region(self) -> str:
        return self.ARN.split(":")[3]

    # @cached_property
    # def labels(self) -> dict:
    #     return pass


def deploy_parameter(
    ssm_client,
    name: str,
    data: T.Union[str, list, dict, T.Any],
    description: T.Optional[str] = None,
    type_is_string: bool = False,
    type_is_string_list: bool = False,
    type_is_secure_string: bool = False,
    kms_key_id: T.Optional[str] = None,
    use_default_kms_key: T.Optional[bool] = False,
    tier_is_standard: bool = False,
    tier_is_advanced: bool = False,
    tier_is_intelligent: bool = False,
    policies: T.Optional[str] = None,
    tags: T.Dict[str, str] = None,
    overwrite: bool = False,
    skip_if_duplicated: bool = True,
) -> T.Optional[Parameter]:
    """
    Create or Update a parameter.

    Ref:

    - put_parameter: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.put_parameter

    :param ssm_client: boto3 system manager client
    :param name: the parameter name
    :param data: the parameter data, could be one of the following:
        - a string
        - a list of string
        - a list of object
        - a dict object
        - arbitrary jsonpicklible python object
    :param description: description of the parameter
    :param type_is_string: is it String type?
    :param type_is_string_list: is it StringList type?
    :param type_is_secure_string: is it SecureString type?
    :param kms_key_id: user defined KMS key id for encryption
    :param use_default_kms_key: if true, then you can omit the ``kms_key_id``
        field, and it will use the default ``alias/aws/ssm`` kms key to encrypt
        your data, and the type become Se
    :param tier_is_standard: is this standard tier?
    :param tier_is_advanced: is this advanced tier?
    :param tier_is_intelligent: is this intelligent tier?
    :param policies: access policy
    :param tags: aws resource tags in python dict
    :param overwrite: if False, then raise error when overwriting an existing parameter
    :param skip_if_duplicated: if True, then won't do deployment if parameter data
        is the same as the one in the latest version.

    :return: None or an :class:`Parameter` object, None means that the deployment
        doesn't happen.
    """
    # --------------------------------------------------------------------------
    # input argument pre processing
    # --------------------------------------------------------------------------
    put_parameter_kwargs = {
        "Name": name,
        "Overwrite": overwrite,
    }

    # type
    ensure_only_one_true(
        [
            ("type_is_string", type_is_string),
            ("type_is_string_list", type_is_string_list),
            ("type_is_secure_string", type_is_secure_string),
        ]
    )

    if type_is_string:
        put_parameter_kwargs["Type"] = ParameterTypeEnum.string.value
    if type_is_string_list:
        put_parameter_kwargs["Type"] = ParameterTypeEnum.string_list.value
    if type_is_secure_string:
        put_parameter_kwargs["Type"] = ParameterTypeEnum.secure_string.value

    # value
    if isinstance(data, str):
        put_parameter_kwargs["Value"] = data
    elif isinstance(data, list):
        if type_is_string_list:
            for item in data:
                if "," in item:
                    raise ValueError(
                        "your parameter data has ',' in it, "
                        "you cannot use StringList type, "
                        "please use String type!"
                    )
            put_parameter_kwargs["Value"] = ",".join(data)
        else:
            put_parameter_kwargs["Value"] = json.dumps(data)
    elif isinstance(data, dict):
        put_parameter_kwargs["Value"] = json.dumps(data)
    else:
        if has_jsonpickle is False:  # pragma: no cover
            raise ImportError(
                "you have to install `jsonpickle` to store arbitrary "
                "python object in AWS Parameter Store."
            )
        put_parameter_kwargs["Value"] = json.dumps(
            {JSON_PICKLE_KEY: jsonpickle.dumps(data)}
        )

    # description
    if description is not None:
        put_parameter_kwargs["Description"] = description

    # encryption related
    with_encryption = False
    if (kms_key_id is not None) and (use_default_kms_key is True):
        raise ValueError(
            "you cannot set `kms_key_id` and `use_default_kms_key = True` "
            "at same time!"
        )
    elif (kms_key_id is not None) and (use_default_kms_key is not True):
        if type_is_secure_string is False:
            raise ValueError(
                f"you cannot set kms_key_id = {kms_key_id!r}, "
                f"use_default_kms_key = {use_default_kms_key!r} "
                f"when type is SecureString!"
            )
        put_parameter_kwargs["KeyId"] = kms_key_id  # pragma: no cover
        with_encryption = True  # pragma: no cover
    elif (kms_key_id is None) and (use_default_kms_key is True):
        if type_is_secure_string is False:
            raise ValueError(
                f"you cannot set kms_key_id = {kms_key_id!r}, "
                f"use_default_kms_key = {use_default_kms_key!r} "
                f"when type is SecureString!"
            )
        put_parameter_kwargs["KeyId"] = DEFAULT_KMS_KEY
        with_encryption = True
    elif (kms_key_id is None) and (use_default_kms_key is not True):
        if type_is_secure_string is True:
            put_parameter_kwargs["KeyId"] = DEFAULT_KMS_KEY
            with_encryption = True
    else:  # pragma: no cover
        raise NotImplementedError

    # tier
    ensure_only_one_true(
        [
            ("tier_is_standard", tier_is_standard),
            ("tier_is_advanced", tier_is_advanced),
            ("tier_is_intelligent", tier_is_intelligent),
        ]
    )

    if tier_is_standard:
        put_parameter_kwargs["Tier"] = ParameterTierEnum.standard.value
    if tier_is_advanced:
        put_parameter_kwargs["Tier"] = ParameterTierEnum.advanced.value
    if tier_is_intelligent:
        put_parameter_kwargs["Tier"] = ParameterTierEnum.intelligent_tiering.value

    # policy
    if policies is not None:  # pragma: no cover
        put_parameter_kwargs["Policies"] = policies

    # tag
    if tags is None:
        tags = dict()
    Tags = [{"Key": k, "Value": v} for k, v in tags.items()]
    if len(Tags):
        put_parameter_kwargs["Tags"] = Tags

    # overwrite
    if overwrite:
        put_parameter_kwargs["Overwrite"] = overwrite

    # --------------------------------------------------------------------------
    # create or update
    # --------------------------------------------------------------------------
    # check duplication
    if skip_if_duplicated:
        # check if parameter exists
        parameter = Parameter.load(
            ssm_client=ssm_client,
            name=name,
            with_decryption=with_encryption,
        )
        # if not exists, do create
        if parameter is None:
            response = ssm_client.put_parameter(**put_parameter_kwargs)
            return Parameter._from_put_parameter_response(
                put_parameter_kwargs, response
            )
        # if already exists, compare the parameter data
        else:
            # if the same, do nothing
            if parameter.Value == put_parameter_kwargs["Value"]:
                return None
            # if not same, do update
            else:
                response = ssm_client.put_parameter(**put_parameter_kwargs)
                return Parameter._from_put_parameter_response(
                    put_parameter_kwargs, response
                )
    # don't duplication check, just update
    else:
        response = ssm_client.put_parameter(**put_parameter_kwargs)
        return Parameter._from_put_parameter_response(put_parameter_kwargs, response)


def delete_parameter(
    ssm_client,
    name: str,
) -> bool:
    """
    Delete a Parameter.

    Ref:

    - delete_parameter: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.delete_parameter

    :return: a boolean value to indicate whether a deletion happened.
    """
    try:
        ssm_client.delete_parameter(Name=name)
        return True
    except Exception as e:
        if "ParameterNotFound" in str(e):
            return False
        else:  # pragma: no cover
            raise e
