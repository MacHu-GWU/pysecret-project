# -*- coding: utf-8 -*-

from pysecret.sh_helper import append_line_if_not_exists
from pysecret.sh_helper import load_var_value_from_shell_script_content
from pysecret.sh_helper import load_var_value_from_shell_script

from pathlib import Path
from pysecret.paths import path_enum


def test_append_line_if_not_exists():
    path_shell_script: Path = path_enum.dir_unit_test.joinpath("env-var.sh")
    path: str = str(path_shell_script)

    append_line_if_not_exists(path, 'export var1="value1"')
    append_line_if_not_exists(path, 'export var1="value1"')
    append_line_if_not_exists(path, 'export var2="value2"')

    assert path_shell_script.read_text().strip().splitlines() == [
        'export var1="value1"',
        'export var2="value2"',
    ]

    environ = load_var_value_from_shell_script(path)
    assert environ == {"var1": "value1", "var2": "value2"}

    path_shell_script.unlink()


test_sh_content = """
export var1="value1"
export  var2="value2" # not valid
export var3 = "value3" # not valid
    export var4="value4" # not valid
# export var5="value5" # not valid
"""


def test_load_var_value_from_shell_script_content():
    environ = load_var_value_from_shell_script_content(test_sh_content)
    assert environ == {"var1": "value1"}


if __name__ == "__main__":
    from pysecret.tests import run_cov_test

    run_cov_test(
        __file__,
        "pysecret.sh_helper",
        preview=False,
    )
