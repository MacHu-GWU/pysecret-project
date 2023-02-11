# -*- coding: utf-8 -*-

"""
AWS Key Management Service supportintegration
"""


def kms_symmetric_encrypt(
    kms_client,
    blob: bytes,
    kms_key_id: str,
):
    """
    Use KMS key to encrypt a short text.

    - KMS.Client.encrypt: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html#KMS.Client.encrypt

    :param blob: binary data to encrypt
    :param kms_key_id:

    :rtype: bytes
    """
    return kms_client.encrypt(
        Plaintext=blob,
        KeyId=kms_key_id,
    )["CiphertextBlob"]


def kms_symmetric_decrypt(
    kms_client,
    blob: bytes,
):
    """
    Use KMS key to decrypt a short text.

    :param blob: binary data to decrypt

    :rtype: bytes
    """
    return kms_client.decrypt(CiphertextBlob=blob)["Plaintext"]
