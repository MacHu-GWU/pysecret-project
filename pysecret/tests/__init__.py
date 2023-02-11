# -*- coding: utf-8 -*-

import sys
from .covtest import run_cov_test
from .paths import dir_tests

py_ver = f"{sys.version_info.major}{sys.version_info.minor}"

try:
    from boto_session_manager import BotoSesManager

    bsm = BotoSesManager()
    bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-data"
except ImportError as e: # pragma: no cover
    pass
