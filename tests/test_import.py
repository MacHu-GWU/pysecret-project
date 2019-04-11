# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx


def test():
    import pysecret

    pysecret.home_file_path()
    pysecret.EnvSecret
    pysecret.JsonSecret
    pysecret.DEFAULT_JSON_SECRET_FILE


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
