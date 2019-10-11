# -*- coding: utf-8 -*-

"""
How to use the ``pysecret.AWSSecret`` to create / update / read secrets.
"""

from pysecret import AWSSecret

aws_profile = "eq_sanhe_assume_role"
secret_id = "my-example-secret"
aws = AWSSecret(profile_name=aws_profile)

secret_data = dict(
    host="www.example.com",
    port=1234,
    database="mydatabase",
    username="admin",
    password="mypassword",
    metadata=dict(
        creator="Sanhe",
    )
)

res = aws.deploy_secret(
    name=secret_id,
    secret_data=secret_data,
)
print(res)

aws = AWSSecret(profile_name=aws_profile)
assert aws.get_secret_value(secret_id, "password") == secret_data["password"]
assert aws.get_secret_value(secret_id, "metadata.creator") == secret_data["metadata"]["creator"]
