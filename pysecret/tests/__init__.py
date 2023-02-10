# -*- coding: utf-8 -*-

import sys
from .covtest import run_cov_test
from .paths import dir_tests

py_ver = f"{sys.version_info.major}{sys.version_info.minor}"

try:
    from boto_session_manager import BotoSesManager
    from ..aws import AWSSecret

    bsm = BotoSesManager()
    aws = AWSSecret(boto_session=bsm.boto_ses)
    bucket = f"{bsm.aws_account_id}-{bsm.aws_region}-data"
except ImportError:
    pass
