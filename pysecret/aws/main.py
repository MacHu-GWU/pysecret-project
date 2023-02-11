# -*- coding: utf-8 -*-

"""
This module provides high level API for AWS Key Management Service and
AWS Secret Manager.
"""

import base64
import json

import boto3

try:
    import typing
except:
    pass
from ..js_helper import get_value, strip_comments

JSON_PICKLE_KEY = "__jsonpickle__"


class AWSSecret(object):
    """
    AWS based secret. Support following backend:

    - AWS Key Management Service
    - AWS Parameter Store
    - AWS Secret Manager
    """

    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_session_token=None,
        region_name=None,
        profile_name=None,
        boto_session=None,
    ):
        if boto_session is None:
            self.ses = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
                region_name=region_name,
                profile_name=profile_name,
            )
        else:
            self.ses = boto_session
        self._kms_client = None
        self._sm_client = None
        self._ssm_client = None
        self.secret_cache = dict()
        self.parameter_cache = dict()

    class KMSArgValueEnum:
        class KeyId:
            aws_ssm = "alias/aws/ssm"

    class UpdateModeEnum:
        create = 1
        upsert = 2
        try_create = 3

    class ParameterStoreArgValueEnum:
        class Tier:
            standard = "Standard"
            advanced = "Advanced"
            intelligent_tiering = "Intelligent-Tiering"

    @property
    def kms_client(self):  # Key Management Service client
        if self._kms_client is None:
            self._kms_client = self.ses.client("kms")
        return self._kms_client

    @property
    def sm_client(self):  # Secret Manager client
        if self._sm_client is None:
            self._sm_client = self.ses.client("secretsmanager")
        return self._sm_client

    @property
    def ssm_client(self):  # System Manager client
        if self._ssm_client is None:
            self._ssm_client = self.ses.client("ssm")
        return self._ssm_client

    # --------------------------------------------------------------------------
    # AWS Parameter Store integration
    # --------------------------------------------------------------------------
    def _put_parameter(self, parameter_name, put_parameter_kwargs):
        """
        :type parameter_name: str
        :type put_parameter_kwargs: dict

        :rtype: dict
        """
        response = self.ssm_client.put_parameter(**put_parameter_kwargs)
        self.parameter_cache[parameter_name] = None  # reset cache if upsert success
        return response

    def deploy_parameter(
        self,
        name,
        parameter_data,
        description=None,
        kms_key_id=None,
        use_default_kms_key=False,
        tier=None,
        policies=None,
        tags=None,
        update_mode=UpdateModeEnum.create,
        skip_duplicate=True,
    ):
        """
        Create or Update a parameter.

        - boto3 put_parameter api: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.put_parameter

        :type name: str
        :type parameter_data: dict
        :type description: str
        :type kms_key_id: str
        :type use_default_kms_key: bool
        :param use_default_kms_key: if true, use the default
            ``alias/aws/ssm`` kms key for encryption
        :type tier: str
        :type policies: str
        :type tags: typing.Dict[str, str]
        :type update_mode: int
        :type skip_duplicate: bool

        :rtype: dict

        Update mode:

        1. create: create new parameter, raise error if already exists
        2. upsert: create new parameter, overwrite existing one if already exists,
            if skip_duplicate is True, then won't do deployment if parameter data
            not changed
        3. try_create: create new parameter, silently do nothing if already exists

        update mode code can be accessed from ``AWSSecret.UpdateModeEnum``
        """
        if tags is None:
            tags = dict()
        Tags = [{"Key": k, "Value": v} for k, v in tags.items()]

        put_parameter_kwargs = {
            "Name": name,
            "Value": json.dumps(parameter_data),
            "Type": "String",
            "Tier": "Intelligent-Tiering",
        }
        if description is not None:
            put_parameter_kwargs["Description"] = description
        if (use_default_kms_key is True) and (kms_key_id is not None):
            msg = (
                "you cannot set `use_default_kms_key` and " "`kms_key_id` at same time!"
            )
            raise ValueError(msg)
        if use_default_kms_key:
            kms_key_id = self.KMSArgValueEnum.KeyId.aws_ssm
        if kms_key_id is not None:
            put_parameter_kwargs["Type"] = "SecureString"
            put_parameter_kwargs["KeyId"] = kms_key_id
        if policies is not None:
            put_parameter_kwargs["Policies"] = policies
        if tier is not None:
            put_parameter_kwargs["Tier"] = tier
        if len(Tags):
            put_parameter_kwargs["Tags"] = Tags

        if update_mode == self.UpdateModeEnum.create:
            put_parameter_kwargs["Overwrite"] = False
            return self._put_parameter(name, put_parameter_kwargs)
        elif update_mode == self.UpdateModeEnum.upsert:
            put_parameter_kwargs["Overwrite"] = True
            if skip_duplicate:
                try:
                    if (kms_key_id is not None) or (use_default_kms_key is True):
                        with_encryption = True
                    else:
                        with_encryption = False
                    response = self.ssm_client.get_parameter(
                        Name=name,
                        WithDecryption=with_encryption,
                    )
                    if "Parameter" in response:
                        string_value = response["Parameter"]["Value"]
                    else:  # pragma: no cover
                        raise ValueError("Not a valid get_parameter response!")
                    data = json.loads(strip_comments(string_value))
                    if parameter_data == data:  # duplicate parameter data
                        return {}
                    else:
                        return self._put_parameter(name, put_parameter_kwargs)
                except Exception as e:
                    if "ParameterNotFound" in str(e):
                        return self._put_parameter(name, put_parameter_kwargs)
                    else:
                        raise e
            else:
                return self._put_parameter(name, put_parameter_kwargs)
        elif update_mode == self.UpdateModeEnum.try_create:
            try:
                return self._put_parameter(name, put_parameter_kwargs)
            except Exception as e:
                if "exists" in str(e).lower():
                    return {}
                else:
                    raise e
        else:
            raise ValueError("{} is not a valid update_mode code".format(update_mode))

    def get_parameter_raw_value(
        self,
        name,
        with_encryption=False,
    ):
        """
        Get the raw parameter data in form of string.

        :type name: str
        :param name: aws system manager parameter name

        :type with_encryption: bool
        :param with_encryption: use True if it is a secure string type parameter

        :rtype: str
        """
        response = self.ssm_client.get_parameter(
            Name=name,
            WithDecryption=with_encryption,
        )
        if "Parameter" in response:
            return response["Parameter"]["Value"]
        else:  # pragma: no cover
            raise ValueError("Not a valid get_parameter response!")

    def get_parameter_data(
        self,
        name,
        with_encryption=False,
    ):
        """
        Get the parameter data in form of json dictionary.

        :type name: str
        :param name: aws system manager parameter name

        :type with_encryption: bool
        :param with_encryption: use True if it is a secure string type parameter

        :rtype: dict
        """
        if self.parameter_cache.get(name) is None:
            response = self.ssm_client.get_parameter(
                Name=name,
                WithDecryption=with_encryption,
            )
            if "Parameter" in response:
                string_value = response["Parameter"]["Value"]
            else:  # pragma: no cover
                raise ValueError("Not a valid get_parameter response!")
            data = json.loads(strip_comments(string_value))
            self.parameter_cache[name] = data
        else:
            data = self.parameter_cache[name]
        return data

    def get_parameter_value(
        self,
        name,
        json_path,
        with_encryption=False,
    ):
        """
        Fetch a specific value using json path dot notation

        :type name: str
        :param name: aws system manager parameter name

        :type json_path: str
        :param json_path: json path dot notation

        :type with_encryption: bool
        :param with_encryption: use True if it is a secure string type parameter

        :rtype: str
        :return: parameter value in string
        """
        data = self.get_parameter_data(name, with_encryption)
        return get_value(data, json_path)

    def deploy_parameter_object(
        self,
        name,
        parameter_obj,
        description=None,
        kms_key_id=None,
        use_default_kms_key=False,
        tier=None,
        policies=None,
        tags=None,
        update_mode=UpdateModeEnum.create,
        skip_duplicate=True,
    ):
        """
        Deploy a parameter object implemented using attrs library https://pypi.org/project/attrs/
        to AWS parameter store. It use jsonpickle https://pypi.org/project/attrs/
        library for serialization.

        :type name: str
        :type parameter_obj: typing.Any
        :type description: str
        :type kms_key_id: str
        :type use_default_kms_key: bool
        :param use_default_kms_key: if true, use the default
            ``alias/aws/ssm`` kms key for encryption
        :type tier: str
        :type policies: str
        :type tags: typing.Dict[str, str]
        :type update_mode: int
        :type skip_duplicate: bool

        :rtype: dict

        Update mode:

        1. create: create new parameter, raise error if already exists
        2. upsert: create new parameter, overwrite existing one if already exists,
            if skip_duplicate is True, then won't do deployment if parameter data
            not changed
        3. try_create: create new parameter, silently do nothing if already exists
        """
        import jsonpickle

        parameter_data = {JSON_PICKLE_KEY: jsonpickle.dumps(parameter_obj)}
        return self.deploy_parameter(
            name=name,
            parameter_data=parameter_data,
            description=description,
            kms_key_id=kms_key_id,
            use_default_kms_key=use_default_kms_key,
            tier=tier,
            policies=policies,
            tags=tags,
            update_mode=update_mode,
            skip_duplicate=skip_duplicate,
        )

    def get_parameter_object(
        self,
        name,
        with_encryption=False,
    ):
        import jsonpickle

        data = self.get_parameter_data(
            name=name,
            with_encryption=with_encryption,
        )
        return jsonpickle.loads(data[JSON_PICKLE_KEY])

    def delete_parameter(
        self,
        name: str,
    ) -> dict:  # pragma: no cover
        return self.ssm_client.delete_parameter(Name=name)

    # --------------------------------------------------------------------------
    # AWS Key Management Service integration
    # --------------------------------------------------------------------------
    def kms_symmetric_encrypt(
        self,
        blob,
        kms_key_id,
    ):
        """
        Use KMS key to encrypt a short text.

        - KMS.Client.encrypt: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.encrypt

        :type text_blob: bytes
        :param text_blob:

        :type kms_key_id: str
        :param kms_key_id:

        :rtype: bytes
        """
        return self.kms_client.encrypt(
            Plaintext=blob,
            KeyId=kms_key_id,
        )["CiphertextBlob"]

    def kms_symmetric_decrypt(self, blob):
        """
        Use KMS key to decrypt a short text.

        :type blob: bytes
        :param blobtext: binary data to decrypt

        :rtype: bytes
        """
        return self.kms_client.decrypt(CiphertextBlob=blob)["Plaintext"]

    # --------------------------------------------------------------------------
    # AWS Secret Manager integration
    # --------------------------------------------------------------------------
    def deploy_secret(
        self,
        name,
        secret_data,
        description=None,
        kms_key_id=None,
        tags=None,
        update_mode=UpdateModeEnum.create,
    ):
        """
        Create or Update a AWS Secret.

        - create_secret: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.create_secret
        - update_secret: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.update_secret

        :type name: str
        :type secret_data: dict
        :type description: str
        :type kms_key_id: str
        :type tags: typing.Dict[str, str]
        :type update_mode: int

        Update mode:

        1. create: create new secret, raise error if already exists
        2. upsert: create new secret, overwrite existing one if exists
        3. try create: create new secret, silently do nothing if already exists

        Note:

            don't support Secret binary yet.
        """
        if tags is None:
            tags = dict()
        Tags = [{"Key": k, "Value": v} for k, v in tags.items()]

        create_or_update_secret_kwargs = {"SecretString": json.dumps(secret_data)}
        if description:
            create_or_update_secret_kwargs["Description"] = description
        if kms_key_id:
            create_or_update_secret_kwargs["KmsKeyId"] = kms_key_id
        if Tags:
            create_or_update_secret_kwargs["Tags"] = Tags

        try:  # create secret
            create_or_update_secret_kwargs["Name"] = name
            response = self.sm_client.create_secret(**create_or_update_secret_kwargs)
            self.secret_cache[name] = None
            return response
        except Exception as e:  # update secret
            if "exists" in str(e).lower():
                if update_mode == self.UpdateModeEnum.create:
                    raise e
                elif update_mode == self.UpdateModeEnum.upsert:
                    create_or_update_secret_kwargs.pop("Name")
                    create_or_update_secret_kwargs["SecretId"] = name
                    create_or_update_secret_kwargs.pop("Tags", None)
                    if len(tags):
                        print(
                            "ignore tags because you cannot update tag in `update_secret` API"
                        )
                    response = self.sm_client.update_secret(
                        **create_or_update_secret_kwargs
                    )
                    self.secret_cache[name] = None
                    return response
                elif update_mode == self.UpdateModeEnum.try_create:
                    return {}
                else:
                    raise ValueError(
                        "{} is not a valid update_mode code".format(update_mode)
                    )
            else:
                raise e

    def get_secret_raw_value(self, secret_id):
        """
        Get the raw secret data in form of string or binary.

        :type secret_id: str

        :rtype: typing.Union[str, bytes]
        """
        response = self.sm_client.get_secret_value(SecretId=secret_id)
        if "SecretString" in response:
            return response["SecretString"]
        else:
            return base64.b64decode(response["SecretBinary"])

    def get_secret_data(self, secret_id):
        """
        Get the secret data in form of json dictionary.

        :type secret_id: str
        :param secret_id: aws secret id

        :type key: str
        :param key: secret value dictionary key

        :rtype: dict
        """
        if self.secret_cache.get(secret_id) is None:
            response = self.sm_client.get_secret_value(SecretId=secret_id)
            if "SecretString" in response:
                secret = response["SecretString"]
            else:
                decoded_binary_secret = base64.b64decode(response["SecretBinary"])
                secret = decoded_binary_secret.decode("utf-8")
            data = json.loads(strip_comments(secret))
            self.secret_cache[secret_id] = data
        else:
            data = self.secret_cache[secret_id]
        return data

    def get_secret_value(self, secret_id, json_path):
        """
        Fetch a specific value using json path dot notation

        :type secret_id: str
        :param secret_id: aws secret id

        :type json_path: str
        :param json_path: json path dot notation
        """
        data = self.get_secret_data(secret_id)
        return get_value(data, json_path)

    def deploy_secret_object(
        self,
        name,
        secret_obj,
        description=None,
        kms_key_id=None,
        tags=None,
        update_mode=UpdateModeEnum.create,
    ):
        """
        Deploy a secret object implemented using attrs library https://pypi.org/project/attrs/
        to AWS Secret Manager. It use jsonpickle https://pypi.org/project/attrs/
        library for serialization.

        :type name: str
        :type secret_obj: typing.Any
        :type description: str
        :type kms_key_id: str
        :type tags: typing.Dict[str, str]
        :type update_mode: int

        :rtype: dict

        Update mode:

        1. create: create new parameter, raise error if already exists
        2. upsert: create new parameter, overwrite existing one if exists
        3. try create: create new parameter, silently do nothing if already exists
        """
        import jsonpickle

        secret_data = {JSON_PICKLE_KEY: jsonpickle.dumps(secret_obj)}
        return self.deploy_secret(
            name=name,
            secret_data=secret_data,
            description=description,
            kms_key_id=kms_key_id,
            tags=tags,
            update_mode=update_mode,
        )

    def get_secret_object(self, secret_id):
        import jsonpickle

        data = self.get_secret_data(secret_id)
        return jsonpickle.loads(data[JSON_PICKLE_KEY])

    def delete_secret(
        self,
        secret_id: str,
        recovery_window_in_days=30,
        force_delete_without_recovery=False,
    ) -> dict:  # pragma: no cover
        return self.sm_client.delete_secret(
            SecretId=secret_id,
            RecoveryWindowInDays=recovery_window_in_days,
            force_delete_without_recovery=force_delete_without_recovery,
        )
