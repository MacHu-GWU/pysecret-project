# -*- coding: utf-8 -*-

from pysecret.tests import bsm, run_cov_test
from pysecret.aws.kms import (
    kms_symmetric_encrypt,
    kms_symmetric_decrypt,
)

kms_client = bsm.kms_client
TEST_KMS_KEY_ALIAS = "alias/pysecret_test"


def setup_module(module):
    try:
        kms_client.describe_key(KeyId=TEST_KMS_KEY_ALIAS)
    except Exception as e:
        if "not found" in str(e).lower():
            res = kms_client.create_key()
            key_id = res["KeyMetadata"]["KeyId"]
            kms_client.create_alias(
                AliasName=TEST_KMS_KEY_ALIAS,
                TargetKeyId=key_id,
            )
        else:
            raise e


def test_encrypt_decrypt():
    blob = "hello".encode("utf-8")
    encrypted_blob = kms_symmetric_encrypt(kms_client, blob, TEST_KMS_KEY_ALIAS)
    decrypted_blob = kms_symmetric_decrypt(kms_client, encrypted_blob)
    assert decrypted_blob.decode("utf-8") == "hello"


if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.aws.kms", preview=False)
