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
    from .helper import home_file_path
    from .env import EnvSecret
except ImportError:
    pass
except Exception as e:
    raise e


