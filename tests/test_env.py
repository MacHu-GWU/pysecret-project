# -*- coding: utf-8 -*-

import pytest
from pysecret.env import Env


class TestEnv(object):
    def test(self):
        env = Env()
        env.set("TEST_PYSECRET_NAME", "Alice")
        assert env.get("TEST_PYSECRET_NAME") == "Alice"

        env.apply_source_pysecret_to_bashrc()
        env.apply_source_pysecret_to_bash_profile()
        env.apply_source_pysecret_to_config_fish()
        env.apply_source_pysecret_to_zshrc()


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
