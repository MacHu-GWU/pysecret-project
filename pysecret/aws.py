# -*- coding: utf-8 -*-

"""
This module provides high level API for AWS Key Management Service and
AWS Secret Manager.
"""

import json
import boto3
import base64
from .js_helper import get_value


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
        self.kms_client = self.ses.client("kms")
        self.sm_client = self.ses.client("secretsmanager")
        self.secret_cache = dict()

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

        try:
            create_or_update_secret_kwargs["Name"] = name
            return self.sm_client.create_secret(**create_or_update_secret_kwargs)
        except Exception as e:
            if type(e).__name__ == "ResourceExistsException":
                create_or_update_secret_kwargs.pop("Name")
                create_or_update_secret_kwargs["SecretId"] = name
                return self.sm_client.update_secret(**create_or_update_secret_kwargs)
            else:
                raise e


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
