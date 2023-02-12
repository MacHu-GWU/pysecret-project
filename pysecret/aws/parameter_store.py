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
from .tagging import encode_tags, decode_tags


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


def get_parameter_tags(
    ssm_client,
    name: str,
) -> T.Dict[str, str]:
    """
    Get parameter tags.

    Ref:

    - list_tags_for_resource: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.list_tags_for_resource

    :return: return empty dict if parameter doesn't have tags. otherwise,
        return tags in format of key value dict.
    """
    response = ssm_client.list_tags_for_resource(
        ResourceType="Parameter",
        ResourceId=name,
    )
    return decode_tags(response.get("TagList", []))


def remove_parameter_tags(
    ssm_client,
    name: str,
    tag_keys: T.List[str],
):
    """
    Delete parameter tags.

    Ref:

    - remove_tags_from_resource: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.remove_tags_from_resource
    """
    ssm_client.remove_tags_from_resource(
        ResourceType="Parameter",
        ResourceId=name,
        TagKeys=tag_keys,
    )


def update_parameter_tags(
    ssm_client,
    name: str,
    tags: T.Dict[str, str],
):
    """
    Create or update (partial update) tags.

    Ref:

    - add_tags_to_resource: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.add_tags_to_resource
    """
    ssm_client.add_tags_to_resource(
        ResourceType="Parameter",
        ResourceId=name,
        Tags=encode_tags(tags),
    )


def put_parameter_tags(
    ssm_client,
    name: str,
    tags: T.Optional[T.Dict[str, str]] = None,
):
    """
    Full replacement update tags.

    - if None, then do nothing
    - if empty dict, then delete tags
    - if non-empty dict, then do full replacement update
    """
    if tags is None:
        return

    existing_tags = get_parameter_tags(ssm_client, name)

    if len(tags) == 0:
        if len(existing_tags):  # only run remove tags when there are existing tags
            remove_parameter_tags(ssm_client, name, list(existing_tags))
    else:
        # if to-update tags is super set of the existing tags
        # then no need to run remove tags
        # otherwise, need to run remove tags
        if not (len(set(existing_tags).difference(set(tags))) == 0):
            remove_parameter_tags(ssm_client, name, list(existing_tags))

        ssm_client.add_tags_to_resource(
            ResourceType="Parameter",
            ResourceId=name,
            Tags=encode_tags(tags),
        )


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
    Tags: T.Dict[str, str] = dataclasses.field(default_factory=dict)
    Labels: T.List[str] = dataclasses.field(default_factory=list)

    @classmethod
    def load(
        cls,
        ssm_client,
        name: str,
        version: T.Optional[int] = None,
        label: T.Optional[str] = None,
        with_decryption: T.Optional[bool] = None,
        with_tags: bool = False,
    ) -> T.Optional["Parameter"]:
        """
        Load parameter data.

        :param name: the raw parameter name, don't set version and label here
        :param version: the integer version
        :param label: the string label
        :param with_decryption: is this parameter a secure string?
        :param with_tags: also get resource tags?

        Ref:

        - get_parameter: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.get_parameter
        """
        # preprocess input arguments
        if (version is not None) and (label is not None):  # pragma: no cover
            raise ValueError("You cannot set both `version` and `label`!")
        elif version is not None:
            name = f"{name}:{version}"
        elif label is not None:
            name = f"{name}:{label}"
        else:
            pass

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
                # if forget to set with_description = True, then do it again
                if with_decryption is not True:
                    parameter = cls.load(ssm_client, name, with_decryption=True)
            # if Type is not secure string or already set with_decryption = True
            if with_tags:
                parameter.Tags = get_parameter_tags(ssm_client, name)
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

    def put_label(
        self,
        ssm_client,
        labels: T.List[str],
    ) -> dict:
        """
        Put label to parameter version, this will automatically move label from
        other version if the label already exists.

        Ref:

        - label_parameter_version: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.label_parameter_version
        """
        response = ssm_client.label_parameter_version(
            Name=self.Name,
            ParameterVersion=self.Version,
            Labels=labels,
        )
        self.Labels = labels
        return response

    def delete_label(
        self,
        ssm_client,
        labels: T.List[str],
    ) -> dict:
        """
        Delete labels from parameter version.

        Ref:

        - unlabel_parameter_version: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.unlabel_parameter_version
        """
        response = ssm_client.unlabel_parameter_version(
            Name=self.Name,
            ParameterVersion=self.Version,
            Labels=labels,
        )
        for label in labels:
            if label in self.Labels:
                self.Labels.remove(label)
        return response


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
    tags: T.Optional[T.Dict[str, str]] = None,
    overwrite: bool = False,
    skip_if_duplicated: bool = True,
) -> T.Optional[Parameter]:
    """
    Create or Update a parameter.

    Ref:

    - put_parameter: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.put_parameter

    Note:

        - you cannot change tags when overwriting parameter, you have to call
            ``add_tags_to_resource`` API after overwriting.

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
    :param tags: if None, then don't update tags. if empty dict, then delete tags,
        if non-empty dict, then do full replacement update.
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
                f"when type is NOT SecureString!"
            )
        put_parameter_kwargs["KeyId"] = kms_key_id  # pragma: no cover
        with_encryption = True  # pragma: no cover
    elif (kms_key_id is None) and (use_default_kms_key is True):
        if type_is_secure_string is False:
            raise ValueError(
                f"you cannot set kms_key_id = {kms_key_id!r}, "
                f"use_default_kms_key = {use_default_kms_key!r} "
                f"when type is NOT SecureString!"
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
            if tags:
                put_parameter_kwargs["Tags"] = encode_tags(tags)
            if overwrite:
                put_parameter_kwargs.pop("Overwrite")
            response = ssm_client.put_parameter(**put_parameter_kwargs)
            return Parameter._from_put_parameter_response(
                put_parameter_kwargs, response
            )
        # if already exists, compare the parameter data
        else:
            # if the same, do nothing
            if parameter.Value == put_parameter_kwargs["Value"]:
                put_parameter_tags(ssm_client, name, tags)
                return None
            # if not same, do update
            else:
                response = ssm_client.put_parameter(**put_parameter_kwargs)
                put_parameter_tags(ssm_client, name, tags)
                return Parameter._from_put_parameter_response(
                    put_parameter_kwargs, response
                )
    # don't duplication check, just update
    else:
        response = ssm_client.put_parameter(**put_parameter_kwargs)
        put_parameter_tags(ssm_client, name, tags)
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
