# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx


def test():
    import pysecret

    _ = pysecret.dir_home
    _ = pysecret.path_bash_profile
    _ = pysecret.path_bashrc
    _ = pysecret.path_zshrc

    _ = pysecret.BaseEnvVar
    _ = pysecret.AWSEnvVar

    _ = pysecret.JsonSecret
    _ = pysecret.DEFAULT_JSON_SECRET_FILE

    _ = pysecret.BaseShellScriptSecret

    _ = pysecret.Parameter
    _ = pysecret.deploy_parameter
    _ = pysecret.delete_parameter
    _ = pysecret.get_parameter_tags
    _ = pysecret.update_parameter_tags
    _ = pysecret.put_parameter_tags
    _ = pysecret.remove_parameter_tags

    _ = pysecret.Secret
    _ = pysecret.deploy_secret
    _ = pysecret.delete_secret

    _ = pysecret.kms_symmetric_encrypt
    _ = pysecret.kms_symmetric_decrypt

    with pytest.raises(AttributeError):
        _ = pysecret.AWSSecret

    with pytest.raises(AttributeError):
        _ = pysecret.EnvSecret

    with pytest.raises(AttributeError):
        _ = pysecret.get_home_path


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
