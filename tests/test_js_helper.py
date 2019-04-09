# -*- coding: utf-8 -*-

import os
import pytest
from pysecret import js_helper

json_file = os.path.join(os.path.dirname(__file__), "test.json")


def test_set_value_del_key():
    data = {}

    js_helper.set_value(data, "meta", "profile")
    assert data == {"meta": "profile"}

    js_helper.set_value(data, "alice.name", "Alice")
    js_helper.set_value(data, "alice.dob", "2000-01-01")
    assert data == {"meta": "profile", "alice": {"name": "Alice", "dob": "2000-01-01"}}

    js_helper.set_value(data, "bob.name", "Bob")
    js_helper.set_value(data, "bob.dob", "2000-01-01")

    assert data["bob"]["dob"] == "2000-01-01"
    js_helper.del_key(data, "bob.dob")
    assert "dob" not in data["bob"]

    assert "bob" in data
    js_helper.del_key(data, "bob")
    assert "bob" not in data


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
