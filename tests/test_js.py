# -*- coding: utf-8 -*-

import os
import pytest
from pysecret.js import JsonSecret

TEST_SECRET_FILE = os.path.join(os.path.dirname(__file__), "secret.json")


class TestJsonSecret(object):
    def test(self):
        js = JsonSecret.new(secret_file=TEST_SECRET_FILE)
        js.set_value("mydb.host", "localhost")
        js.set_value("mydb.port", 1234)
        js.set_value("mydb.username", "alice")
        js.set_value("mydb.password", "mypassword")

        assert js.get_value("mydb.password") == "mypassword"


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
