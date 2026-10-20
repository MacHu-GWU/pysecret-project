# -*- coding: utf-8 -*-

"""
Public API. Users import from here::

    from pysecret.api import JsonSecret
    import pysecret.api as pysecret
"""

from .paths import dir_home
from .paths import path_bash_profile
from .paths import path_bashrc
from .paths import path_zshrc
from .env import BaseEnvVar
from .env import AWSEnvVar
from .js import JsonSecret
from .js import DEFAULT_JSON_SECRET_FILE
from .sh import BaseShellScriptSecret
from .aws.parameter_store import Parameter
from .aws.parameter_store import deploy_parameter
from .aws.parameter_store import delete_parameter
from .aws.parameter_store import get_parameter_tags
from .aws.parameter_store import update_parameter_tags
from .aws.parameter_store import put_parameter_tags
from .aws.parameter_store import remove_parameter_tags
from .aws.secret_manager import Secret
from .aws.secret_manager import deploy_secret
from .aws.secret_manager import delete_secret
from .aws.kms import kms_symmetric_encrypt
from .aws.kms import kms_symmetric_decrypt
