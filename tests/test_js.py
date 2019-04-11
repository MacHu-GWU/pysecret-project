# -*- coding: utf-8 -*-

import os
import pytest
from pysecret.js import JsonSecret

TEST_SECRET_JSON_FILE = os.path.join(
    os.path.dirname(__file__), "test_pysecret.json")


def teardown_module(module):
    if os.path.exists(TEST_SECRET_JSON_FILE):
        os.remove(TEST_SECRET_JSON_FILE)


class TestJsonSecret(object):
    def test(self):
        js = JsonSecret.new(secret_file=TEST_SECRET_JSON_FILE)
        js.set("mydb.host", "localhost")
        js.set("mydb.port", 1234)
        js.set("mydb.username", "alice")
        js.set("mydb.password", "mypassword")

        assert js.get("mydb.password") == "mypassword"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
