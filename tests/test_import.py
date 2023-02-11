# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx


def test():
    import pysecret

    _ = pysecret.dir_home
    _ = pysecret.path_bash_profile
    _ = pysecret.path_bashrc
    _ = pysecret.path_zshrc

    _ = pysecret.BaseEnv
    _ = pysecret.AWSEnvVar

    _ = pysecret.JsonSecret
    _ = pysecret.DEFAULT_JSON_SECRET_FILE

    _ = pysecret.BaseShellScriptSecret

    _ = pysecret.Parameter
    _ = pysecret.deploy_parameter
    _ = pysecret.delete_parameter

    _ = pysecret.Secret
    _ = pysecret.deploy_secret
    _ = pysecret.delete_secret


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
