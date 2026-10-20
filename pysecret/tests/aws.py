# -*- coding: utf-8 -*-

"""
Shared objects for the real AWS tests in ``tests_aws/``.

Kept out of ``pysecret.tests`` so that importing it from ``tests/`` never
creates a boto session or calls AWS.
"""

import sys

from boto_session_manager import BotoSesManager

py_ver = f"{sys.version_info.major}{sys.version_info.minor}"

bsm = BotoSesManager()
