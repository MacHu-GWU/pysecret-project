# -*- coding: utf-8 -*-

"""
How to use the ``pysecret.AWSSecret`` to create / update / read secrets.
"""

from pysecret import AWSSecret

aws_profile = "eq_sanhe_assume_role"
# aws_profile = "eq_sanhe"
aws_region = "us-east-1"
aws = AWSSecret(profile_name=aws_profile, region_name=aws_region)

# --- secret manager ---
secret_id = "my-example-secret"
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

# deploy secret to AWS
res = aws.deploy_secret(
    name=secret_id,
    secret_data=secret_data,
)

# read secret from AWS
assert aws.get_secret_value(secret_id, "password") == secret_data["password"]
assert aws.get_secret_value(secret_id, "metadata.creator") == secret_data["metadata"]["creator"]

#--- parameter store
# deploy parameter to AWS
parameter_name = "my-example-parameter"
parameter_data = dict(
    project_name="my-example-project",
    metadata=dict(
        creator="Sanhe",
    ),
)
aws.deploy_parameter(
    name=parameter_name,
    parameter_data=parameter_data,
)

# read parameter from AWS
assert aws.get_parameter_value(parameter_name, "project_name") == parameter_data["project_name"]
assert aws.get_parameter_value(parameter_name, "metadata.creator") == parameter_data["metadata"]["creator"]
