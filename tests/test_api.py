# -*- coding: utf-8 -*-

from pysecret import api


def test():
    _ = api
    _ = api.dir_home
    _ = api.path_bash_profile
    _ = api.path_bashrc
    _ = api.path_zshrc
    _ = api.BaseEnvVar
    _ = api.AWSEnvVar
    _ = api.JsonSecret
    _ = api.DEFAULT_JSON_SECRET_FILE
    _ = api.BaseShellScriptSecret
    _ = api.Parameter
    _ = api.deploy_parameter
    _ = api.delete_parameter
    _ = api.get_parameter_tags
    _ = api.update_parameter_tags
    _ = api.put_parameter_tags
    _ = api.remove_parameter_tags
    _ = api.Secret
    _ = api.deploy_secret
    _ = api.delete_secret
    _ = api.kms_symmetric_encrypt
    _ = api.kms_symmetric_decrypt


if __name__ == "__main__":
    from pysecret.tests import run_cov_test

    run_cov_test(
        __file__,
        "pysecret.api",
        preview=False,
    )
