# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from pysecret.singleton import CachedSpam


class Logger(CachedSpam):
    def __real_init__(self, name):
        self.name = name

    def info(self, msg):
        pass


class Config(CachedSpam):
    def __real_init__(self, name):
        self.name = name


def test():
    with raises(RuntimeError):
        Logger("system")

    logger1 = Logger.new("system")
    logger2 = Logger.new("system")
    logger3 = Logger.new("user")
    assert logger1 is logger2
    assert logger1 is not logger3

    config1 = Config.new("system")
    config2 = Config.new("system")
    config3 = Config.new("user")
    assert config1 is config2
    assert config1 is not config3

    assert Logger._cache is not Config._cache
    assert isinstance(Logger._cache["system"], Logger)
    assert isinstance(Config._cache["system"], Config)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
