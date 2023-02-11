# -*- coding: utf-8 -*-

from boto_session_manager import BotoSesManager
from pysecret.tests import bsm, run_cov_test
from pysecret.env import AWSEnvVar


class TestAWSEnvVar:
    def test(self):
        # before
        aws = AWSEnvVar.load()
        assert aws.AWS_ACCESS_KEY_ID is None

        # with env var
        response = bsm.sts_client.get_session_token()

        aws_access_key_id = response["Credentials"]["AccessKeyId"]
        aws_secret_access_key = response["Credentials"]["SecretAccessKey"]
        aws_session_token = response["Credentials"]["SessionToken"]

        new_bsm = BotoSesManager(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            region_name=bsm.aws_region,
        )

        with new_bsm.awscli():
            aws = AWSEnvVar.load()
            assert aws.AWS_ACCESS_KEY_ID == aws_access_key_id
            assert aws.AWS_SECRET_ACCESS_KEY == aws_secret_access_key
            assert aws.AWS_SESSION_TOKEN == aws_session_token

            aws.to_json()

        # after
        aws = AWSEnvVar.load()
        assert aws.AWS_ACCESS_KEY_ID is None


if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.env", preview=False)
