# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from pysecret.tests import run_cov_test

    run_cov_test(
        __file__,
        "pysecret.aws",
        is_folder=True,
        preview=False,
    )
