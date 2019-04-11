# -*- coding: utf-8 -*-

import pytest
from pytest import raises, approx
from pysecret.env_helper import load_var_value_from_shell_script_content

test_content = """
export var1="value1"
export  var2="value2"
export var3 = "value3"
    export var4="value4"
# export var5="value5"
"""


def test_load_var_value_from_shell_script_content():
    environ = load_var_value_from_shell_script_content(test_content)
    assert environ == {"var1": "value1"}


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
