# -*- coding: utf-8 -*-

from pysecret.js_helper import (
    create_json_if_not_exists,
    set_value,
    get_value,
    del_key,
)
from pysecret.tests import run_cov_test, dir_tests

path_json = dir_tests.joinpath("test.json")


def test_create_json_if_not_exists():
    # before
    if path_json.exists():
        path_json.unlink()
    assert path_json.exists() is False

    # run
    create_json_if_not_exists(f"{path_json}")

    # after
    assert path_json.exists() is True
    assert path_json.read_text() == "{}"

    # clean up
    path_json.unlink(missing_ok=True)


def test_set_value_del_key():
    data = {}

    res = set_value(data, "meta", "profile")
    assert data == {"meta": "profile"}
    assert res == {"meta": "profile"}

    set_value(data, "alice.name", "Alice")
    res = set_value(data, ".alice.dob", "2000-01-01")
    assert data == {"meta": "profile", "alice": {"name": "Alice", "dob": "2000-01-01"}}
    assert res == {"meta": "profile", "alice": {"name": "Alice", "dob": "2000-01-01"}}
    assert get_value(data, "alice.name") == "Alice"
    assert get_value(data, ".alice.dob") == "2000-01-01"
    assert get_value(data, ".") == {
        "meta": "profile",
        "alice": {"name": "Alice", "dob": "2000-01-01"},
    }

    del_key(data, "alice.dob")
    assert "dob" not in data["alice"]
    assert "alice" in data
    del_key(data, "alice")
    assert "alice" not in data

    new_data = set_value(data, ".", {})
    assert new_data == {}


if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.js_helper", preview=False)
