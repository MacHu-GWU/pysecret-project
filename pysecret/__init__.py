# -*- coding: utf-8 -*-

"""
pysecret is a tiny library to allow developer load secret information safely.

- from environment variable
- from json file
- from AWS Secret Manager and Key Management Service
"""

from ._version import __version__

__short_description__ = "utility tool that load secret information safely."
__license__ = "MIT"
__author__ = "Sanhe Hu"
__author_email__ = "husanhe@gmail.com"
__github_username__ = "MacHu-GWU"

try:
    from .paths import (
        dir_home,
        path_bash_profile,
        path_bashrc,
        path_zshrc,
    )
    from .env import (
        BaseEnvVar,
        AWSEnvVar,
    )
    from .js import (
        JsonSecret,
        DEFAULT_JSON_SECRET_FILE,
    )
    from .sh import BaseShellScriptSecret
except ImportError:  # pragma: no cover
    pass
except Exception as e:  # pragma: no cover
    raise e

try:
    from .aws import (
        Parameter,
        deploy_parameter,
        delete_parameter,
        get_parameter_tags,
        update_parameter_tags,
        put_parameter_tags,
        remove_parameter_tags,
        Secret,
        deploy_secret,
        delete_secret,
        kms_symmetric_encrypt,
        kms_symmetric_decrypt,
    )
except ImportError:  # pragma: no cover
    pass
except Exception as e:  # pragma: no cover
    raise e


def __getattr__(name: str):  # pragma: no cover
    if name in [
        "EnvSecret",
        "get_home_path",
        "AWSSecret",
    ]:
        raise AttributeError(
            f"The pysecret.{name} API has been removed since 2.X! "
            f"You can either downgrade to 1.0.4 or update your code."
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
