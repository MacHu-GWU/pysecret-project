# -*- coding: utf-8 -*-

import pytest
from pysecret import AWSSecret

aws = AWSSecret()

TEST_KMS_KEY_ALIAS = "alias/pysecret_test"


def setup_module(module):
    try:
        aws.kms_client.describe_key(KeyId=TEST_KMS_KEY_ALIAS)
    except Exception as e:
        if "not found" in str(e).lower():
            res = aws.kms_client.create_key()
            key_id = res["KeyMetadata"]["KeyId"]
            aws.kms_client.create_alias(AliasName=TEST_KMS_KEY_ALIAS, TargetKeyId=key_id)
        else:
            raise e


def test_encrypt_decrypt():
    blob = "hello".encode("utf-8")
    encrypted_blob = aws.kms_symmetric_encrypt(blob, TEST_KMS_KEY_ALIAS)
    decrypted_blob = aws.kms_symmetric_decrypt(encrypted_blob)
    assert decrypted_blob.decode("utf-8") == "hello"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
