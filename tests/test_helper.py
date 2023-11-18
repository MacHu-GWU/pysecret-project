# -*- coding: utf-8 -*-

import pytest
from pysecret.helper import (
    ensure_only_one_true,
)
from pysecret.tests import run_cov_test


def test_ensure_only_one_true():
    ensure_only_one_true(
        [
            ("abc", True),
            ("xyz", False),
        ]
    )
    with pytest.raises(ValueError) as e:
        ensure_only_one_true(
            [
                ("abc", True),
                ("xyz", True),
            ]
        )


if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.helper", preview=False)
