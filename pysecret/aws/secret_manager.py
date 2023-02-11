# -*- coding: utf-8 -*-

"""
AWS Secret Manager support.
"""

import typing as T
import json

import dataclasses
from datetime import datetime

from ..compat import cached_property
from ..js_helper import strip_comments


@dataclasses.dataclass
class Secret:
    """
    AWS Secret Manager secret object.

    - The camel case attributes are raw value from AWS API.
    - The snake case attributes are user-friendly accessor to the data.
    - only one of ``SecretBinary`` or ``SecretString`` could exist.
    - if you know what data type to expect in the secret, please use
        :meth:`Secret.binary`, :meth:`Secret.string`, :meth:`Secret.json_dict`,
        :meth:`Secret.json_list` to access the data.
    """
    ARN: str = dataclasses.field()
    Name: str = dataclasses.field()
    VersionId: str = dataclasses.field()
    CreatedDate: datetime = dataclasses.field()
    SecretBinary: T.Optional[bytes] = dataclasses.field(default=None)
    SecretString: T.Optional[str] = dataclasses.field(default=None)
    VersionStages: T.List[str] = dataclasses.field(default_factory=list)

    @cached_property
    def fingerprint(self) -> bytes:
        """
        The fingerprint of the content. Can be used for comparison.
        """
        if self.SecretBinary is not None:
            return self.SecretBinary
        else:
            return self.SecretString.encode("utf-8")

    @classmethod
    def load(
        cls,
        sm_client,
        name_or_arn: str,
        version_id: T.Optional[str] = None,
        version_stage: T.Optional[str] = None,
    ) -> T.Optional["Secret"]:
        """
        Load secret data.

        Ref:

        - describe_secret: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.describe_secret
        - get_secret_value: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.get_secret_value
        - list_secret_version_ids: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.list_secret_version_ids
        """
        # --- resolve arguments
        kwargs = dict(SecretId=name_or_arn)
        if version_id:  # pragma: no cover
            kwargs["VersionId"] = version_id
        if version_id:  # pragma: no cover
            kwargs["VersionStage"] = version_stage

        try:
            response = sm_client.get_secret_value(**kwargs)
            return cls(
                ARN=response["ARN"],
                Name=response["Name"],
                VersionId=response["VersionId"],
                SecretBinary=response.get("SecretBinary"),
                SecretString=response.get("SecretString"),
                CreatedDate=response["CreatedDate"],
                VersionStages=response.get("VersionStages", []),
            )
        except Exception as e:
            if "ResourceNotFoundException" in str(e):
                return None
            else:  # pragma: no cover
                raise e

    @classmethod
    def _from_create_or_update_secret_response(
        cls,
        create_or_update_secret_kwargs: dict,
        create_or_update_secret_response: dict,
    ):
        return Secret(
            ARN=create_or_update_secret_response["ARN"],
            Name=create_or_update_secret_response["Name"],
            VersionId=create_or_update_secret_response["VersionId"],
            SecretBinary=create_or_update_secret_kwargs.get("SecretBinary"),
            SecretString=create_or_update_secret_kwargs.get("SecretString"),
            CreatedDate=datetime.strptime(
                create_or_update_secret_response["ResponseMetadata"]["HTTPHeaders"][
                    "date"
                ],
                "%a, %d %b %Y %H:%M:%S %Z",
            ),
        )

    @property
    def binary(self) -> bytes:
        """
        The binary user data.
        """
        return self.SecretBinary

    @property
    def string(self) -> str:
        """
        The string user data.
        """
        return self.SecretString

    @cached_property
    def json_dict(self) -> dict:
        """
        The python dict user data.
        """
        return json.loads(strip_comments(self.SecretString))

    @cached_property
    def json_list(self) -> list:  # pragma: no cover
        """
        The python list user data.
        """
        return json.loads(strip_comments(self.SecretString))

    @property
    def aws_account_id(self) -> str:
        """
        The aws account id of this secret.
        """
        return self.ARN.split(":")[4]

    @property
    def aws_region(self) -> str:
        """
        The aws region of this secret.
        """
        return self.ARN.split(":")[3]


def deploy_secret(
    sm_client,
    name_or_arn: str,
    data: T.Union[bytes, str, list, dict, T.Any],
    description: T.Optional[str] = None,
    kms_key_id: T.Optional[str] = None,
    tags: T.Optional[T.Dict[str, str]] = None,
    add_replica_regions: T.Optional[T.List[T.Dict[str, str]]] = None,
    force_overwrite_replica_secret: T.Optional[bool] = None,
    client_request_token: T.Optional[str] = None,
    skip_if_duplicated: bool = True,
) -> T.Optional[Secret]:
    """
    Create or Update an AWS Secret.

    - create_secret: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.create_secret
    - update_secret: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.update_secret
    - tag_resource: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.tag_resource
    - untag_resource: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.untag_resource

    Note:

        secret manager can only add tag in creation, update_secret doesn't
        support tagging, this function will automatically call ``tag_resource``
        API when needed.

    :param sm_client: the boto3 secretmanager client.
    :param name_or_arn: name or the ARN of this secret.
    :param data: secret data you want to store, currently it supports bytes,
        string, json serializable dict or list.
    :param description: description of this secret.
    :param kms_key_id: the KMS key id you want to use for encryption, by default
        it uses the AWS managed KMS key.
    :param tags: the key value pair of the AWS resource tags.
    :param add_replica_regions: see official document.
    :param force_overwrite_replica_secret: see official document.
    :param client_request_token: see official document.
    :param skip_if_duplicated: default True, if True, will compare the secret data
        to the existing one before deployment. If they are the same, then
        no deployment happens.

    :return: None or an :class:`Secret` object, None means that the deployment
        doesn't happen.
    """
    # --------------------------------------------------------------------------
    # input argument pre processing
    # --------------------------------------------------------------------------
    create_or_update_secret_kwargs = dict()

    # data
    if isinstance(data, bytes):
        create_or_update_secret_kwargs["SecretBinary"] = data
    elif isinstance(data, str):
        create_or_update_secret_kwargs["SecretString"] = data
    elif isinstance(data, (list, dict)):
        create_or_update_secret_kwargs["SecretString"] = json.dumps(data)
    else:  # pragma: no cover
        raise NotImplementedError

    # description
    if description:
        create_or_update_secret_kwargs["Description"] = description

    # kms key id
    if kms_key_id:  # pragma: no cover
        create_or_update_secret_kwargs["KmsKeyId"] = kms_key_id

    # tags
    if tags is None:
        tags = dict()
    tags_ = [{"Key": k, "Value": v} for k, v in tags.items()]

    # --------------------------------------------------------------------------
    # create or update
    # --------------------------------------------------------------------------
    secret = Secret.load(
        sm_client,
        name_or_arn=name_or_arn,
    )
    is_create = secret is None

    # create branch
    if is_create:
        create_or_update_secret_kwargs["Name"] = name_or_arn
        if len(tags_):
            create_or_update_secret_kwargs["Tags"] = tags_
        if add_replica_regions is not None:  # pragma: no cover
            create_or_update_secret_kwargs["AddReplicaRegions"] = add_replica_regions
        if force_overwrite_replica_secret is not None:  # pragma: no cover
            create_or_update_secret_kwargs[
                "ForceOverwriteReplicaSecret"
            ] = add_replica_regions
        if client_request_token is not None:  # pragma: no cover
            create_or_update_secret_kwargs["ClientRequestToken"] = client_request_token
        response = sm_client.create_secret(**create_or_update_secret_kwargs)
        secret = Secret._from_create_or_update_secret_response(
            create_or_update_secret_kwargs=create_or_update_secret_kwargs,
            create_or_update_secret_response=response,
        )
        return secret

    # update branch
    # check duplication
    if skip_if_duplicated:
        # find existing secret's fingerprint
        if "SecretBinary" in create_or_update_secret_kwargs:
            fingerprint = create_or_update_secret_kwargs["SecretBinary"]
        else:
            fingerprint = create_or_update_secret_kwargs["SecretString"].encode("utf-8")
        # if the same, do nothing
        if fingerprint == secret.fingerprint:
            return None

    create_or_update_secret_kwargs["SecretId"] = name_or_arn
    response = sm_client.update_secret(**create_or_update_secret_kwargs)
    secret = Secret._from_create_or_update_secret_response(
        create_or_update_secret_kwargs=create_or_update_secret_kwargs,
        create_or_update_secret_response=response,
    )

    # do tagging
    if tags_ is not None:
        sm_client.tag_resource(SecretId=name_or_arn, Tags=tags_)

    return secret


def delete_secret(
    sm_client,
    name_or_arn: str,
    recovery_window_in_days: T.Optional[int] = None,
    force_delete_without_recovery: T.Optional[bool] = None,
) -> bool:
    """
    Delete a Secret.

    Ref:

    - delete_secret: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html#SecretsManager.Client.delete_secret

    :param sm_client: the boto3 secretmanager client.
    :param name_or_arn: name or the ARN of this secret.
    :param recovery_window_in_days: see official document.
    :param force_delete_without_recovery: see official document.

    :return: a boolean value to indicate whether a deletion happened.
    """
    kwargs = dict(SecretId=name_or_arn)
    if recovery_window_in_days is not None:  # pragma: no cover
        kwargs["RecoveryWindowInDays"] = recovery_window_in_days
    if force_delete_without_recovery is not None:
        kwargs["ForceDeleteWithoutRecovery"] = force_delete_without_recovery
    try:
        sm_client.delete_secret(**kwargs)
        return True
    except Exception as e:
        if "ResourceNotFoundException" in str(e):
            return False
        else:  # pragma: no cover
            raise e
