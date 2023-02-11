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
        BaseEnv,
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
        Secret,
        deploy_secret,
        delete_secret,
    )
except ImportError:  # pragma: no cover
    pass
except Exception as e:  # pragma: no cover
    raise e
