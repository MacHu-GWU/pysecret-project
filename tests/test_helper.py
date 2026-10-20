# -*- coding: utf-8 -*-

from pysecret.helper import ensure_only_one_true

import pytest


def test_ensure_only_one_true():
    ensure_only_one_true(
        [
            ("abc", True),
            ("xyz", False),
        ]
    )
    with pytest.raises(ValueError):
        ensure_only_one_true(
            [
                ("abc", True),
                ("xyz", True),
            ]
        )


if __name__ == "__main__":
    from pysecret.tests import run_cov_test

    run_cov_test(
        __file__,
        "pysecret.helper",
        preview=False,
    )
