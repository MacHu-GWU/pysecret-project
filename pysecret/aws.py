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
from .js_helper import get_value, strip_comments


class AWSSecret(object):
    """
    An AWS Secret syntax simplifier class.
    """

    def __init__(self,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_session_token=None,
                 region_name=None,
                 botocore_session=None,
                 profile_name=None):
        self.ses = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
            botocore_session=botocore_session,
            profile_name=profile_name,
        )
        self._kms_client = None
        self._sm_client = None
        self._ssm_client = None
        self.secret_cache = dict()
        self.parameter_cache = dict()

    @property
    def kms_client(self):
        if self._kms_client is None:
            self._kms_client = self.ses.client("kms")
        return self._kms_client

    @property
    def sm_client(self):
        if self._sm_client is None:
            self._sm_client = self.ses.client("secretsmanager")
        return self._sm_client

    @property
    def ssm_client(self):
        if self._ssm_client is None:
            self._ssm_client = self.ses.client("ssm")
        return self._ssm_client

    def kms_encrypt(self, kms_key_id, text):
        """
        Use KMS key to encrypt a short text.

        :type kms_key_id: str
        :param kms_key_id:

        :type text: str
        :param text:

        :rtype: str
        """
        return base64.b64encode(
            self.kms_client.encrypt(
                KeyId=kms_key_id,
                Plaintext=base64.b64encode(text.encode("utf-8")),
            )["CiphertextBlob"]
        ).decode("utf-8")

    def kms_decrypt(self, text):
        """
        Use KMS key to decrypt a short text.

        :type text: str
        :param text: text to decrypt

        :rtype: str
        """
        return base64.b64decode(self.kms_client.decrypt(
            CiphertextBlob=base64.b64decode(text.encode("utf-8"))
        )["Plaintext"]).decode("utf-8")

    def get_secret_value(self, secret_id, key):
        """
        Fetch a specific secret value

        :type secret_id: str
        :param secret_id: aws secret id

        :type key: str
        :param key: secret value dictionary key

        :rtype: str
        :return: secret value in string
        """
        if self.secret_cache.get(secret_id) is None:
            response = self.sm_client.get_secret_value(SecretId=secret_id)
            if "SecretString" in response:
                secret = response["SecretString"]
            else:
                decoded_binary_secret = base64.b64decode(response["SecretBinary"])
                secret = decoded_binary_secret
            data = json.loads(secret)
            self.secret_cache[secret_id] = data
        else:
            data = self.secret_cache[secret_id]
        return get_value(data, key)

    def deploy_secret(self,
                      name,
                      secret_data,
                      description=None,
                      kms_key_id=None,
                      tags=None):
        """
        Create or Update a AWS Secret.

        - create_secret: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.create_secret
        - update_secret: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.update_secret
        """
        if tags is None:
            tags = dict()
        Tags = [
            {"Key": k, "Value": v}
            for k, v in tags.items()
        ]

        create_or_update_secret_kwargs = {"SecretString": json.dumps(secret_data)}
        if description:
            create_or_update_secret_kwargs["Description"] = description
        if kms_key_id:
            create_or_update_secret_kwargs["KmsKeyId"] = kms_key_id
        if Tags:
            create_or_update_secret_kwargs["Tags"] = Tags

        try: # create secret
            create_or_update_secret_kwargs["Name"] = name
            response = self.sm_client.create_secret(**create_or_update_secret_kwargs)
            self.secret_cache[name] = None
            return response
        except Exception as e: # update secret
            if type(e).__name__ == "ResourceExistsException":
                create_or_update_secret_kwargs.pop("Name")
                create_or_update_secret_kwargs.pop("Tags", None)
                create_or_update_secret_kwargs["SecretId"] = name
                response = self.sm_client.update_secret(**create_or_update_secret_kwargs)
                self.secret_cache[name] = None
                return response
            else:
                raise e

    def get_parameter_value(self,
                            parameter_name,
                            key,
                            with_encryption=False):
        """
        Fetch a specific parameter value

        :type parameter_name: str
        :param parameter_name: aws system manager parameter name

        :type key: str
        :param key: parameter value dictionary key

        :type with_encryption: bool

        :rtype: str
        :return: parameter value in string
        """
        if self.parameter_cache.get(parameter_name) is None:
            response = self.ssm_client.get_parameter(
                Name=parameter_name,
                WithDecryption=with_encryption,
            )
            if "Parameter" in response:
                string_value = response["Parameter"]["Value"]
            else:
                raise ValueError("Not a valid get_parameter response!")
            data = json.loads(string_value)
            self.parameter_cache[parameter_name] = data
        else:
            data = self.parameter_cache[parameter_name]
        return get_value(data, key)

    def deploy_parameter(self,
                         name,
                         parameter_data,
                         description=None,
                         kms_key_id=None,
                         policies=None,
                         tags=None):
        """
        Update parameter.

        - pub_parameter: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html#SSM.Client.put_parameter

        :type name: str
        :type parameter_data: dict
        :type description: str
        :type kms_key_id: str
        :type policies: str
        :type tags: dict
        :rtype: dict
        """
        if tags is None:
            tags = dict()
        Tags = [
            {"Key": k, "Value": v}
            for k, v in tags.items()
        ]
        put_paramter_kwargs = {
            "Name": name,
            "Value": json.dumps(parameter_data),
            "Type": "String",
            "Overwrite": True,
            "Tier": "Intelligent-Tiering",
        }
        if description:
            put_paramter_kwargs["Description"] = description
        if kms_key_id:
            put_paramter_kwargs["Type"] = "SecureString"
            put_paramter_kwargs["KeyId"] = kms_key_id
        if policies:
            put_paramter_kwargs["Policies"] = policies
        if Tags:
            put_paramter_kwargs["Tags"] = Tags

        response = self.ssm_client.put_parameter(**put_paramter_kwargs)
        self.parameter_cache[name] = None
        return response


if __name__ == "__main__":
    aws_profile = "sanhe"
    kms_key_id = "a1679e4b-f415-4aa6-9637-5bee18f9eb64"

    aws = AWSSecret(profile_name=aws_profile)
    secret = "Hello World"
    encrypted_text = aws.kms_encrypt(kms_key_id, secret)
    decrypted_text = aws.kms_decrypt(encrypted_text)
    assert secret != encrypted_text
    assert secret == decrypted_text

    secret_name = "dev/learn-secret-manager"
    assert aws.get_secret_value(secret_name, "a") == "1"
