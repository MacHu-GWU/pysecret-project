# -*- coding: utf-8 -*-

import json
import boto3
import base64


class AWSSecret(object):
    def __init__(self,
                 aws_access_key_id=None,
                 aws_secret_access_key=None,
                 aws_session_token=None,
                 region_name=None,
                 botocore_session=None,
                 profile_name=None):
        ses = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=region_name,
            botocore_session=botocore_session,
            profile_name=profile_name,
        )
        self.kms_client = boto3.client("kms")
        self.sm_client = ses.client("secretsmanager")
        self.secret_cache = dict()

    def kms_encrypt(self, kms_key_id, text):
        return base64.b64encode(
            self.kms_client.encrypt(
                KeyId=kms_key_id,
                Plaintext=base64.b64encode(text.encode("utf-8")),
            )["CiphertextBlob"]
        ).decode("utf-8")

    def kms_decrypt(self, text):
        return base64.b64decode(self.kms_client.decrypt(
            CiphertextBlob=base64.b64decode(text.encode("utf-8"))
        )["Plaintext"]).decode("utf-8")

    def get_secret_value(self, secret_id, key):
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
        return data[key]


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
