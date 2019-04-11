# -*- coding: utf-8 -*-

import os
import pytest
from pysecret.env import EnvSecret

TEST_PYSECRET_INIT_FILE = os.path.join(
    os.path.dirname(__file__), "test_pysecret_init.sh")
TEST_PYSECRET_INIT_FILE_CONTENT = """
export test_pysecret_var1="value1"
export test_pysecret_var2="value2"
export test_pysecret_var3="value3"
"""


def setup_module(module):
    with open(TEST_PYSECRET_INIT_FILE, "wb") as f:
        f.write(TEST_PYSECRET_INIT_FILE_CONTENT.encode("utf-8"))


def teardown_module(module):
    if os.path.exists(TEST_PYSECRET_INIT_FILE):
        os.remove(TEST_PYSECRET_INIT_FILE)


class TestEnv(object):
    def test(self):
        env = EnvSecret()
        env.pysecret_script = TEST_PYSECRET_INIT_FILE

        env.set("test_pysecret_var4", "value4")
        env.set("test_pysecret_var4", "value4")
        env.set("test_pysecret_var4", "value4")
        assert env.get("test_pysecret_var4") == "value4"

        # it is not been loaded to env yet
        assert "test_pysecret_var1" not in os.environ

        # now it is here
        env.load_pysecret_script()
        assert "test_pysecret_var1" in os.environ

        env = EnvSecret()
        env.apply_source_pysecret_to_bashrc()
        env.apply_source_pysecret_to_bash_profile()
        env.apply_source_pysecret_to_config_fish()
        env.apply_source_pysecret_to_zshrc()


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
