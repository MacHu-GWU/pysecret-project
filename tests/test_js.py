# -*- coding: utf-8 -*-

from pysecret.js import JsonSecret
from pysecret.tests import run_cov_test, dir_tests

TEST_SECRET_JSON_FILE = dir_tests.joinpath("test_pysecret.json")


class TestJsonSecret(object):
    def test(self):
        js = JsonSecret.new(secret_file=TEST_SECRET_JSON_FILE)

        js.set("mydb.host", "localhost")
        js.set("mydb.port", 1234)
        js.set("mydb.username", "alice")
        res = js.set("mydb.password", "mypassword")
        assert res == {
            "mydb": {
                "host": "localhost",
                "port": 1234,
                "username": "alice",
                "password": "mypassword",
            }
        }

        assert js.get("mydb.username") == "alice"
        assert js.get("mydb.password") == "mypassword"

        assert "password" in js.get("mydb")
        js.unset("mydb.password")
        assert "password" not in js.get("mydb")

        # clean up
        TEST_SECRET_JSON_FILE.unlink()


if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.js", preview=False)
