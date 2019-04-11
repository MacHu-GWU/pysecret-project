# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from pysecret.singleton import CachedSpam


class BadLogger1(CachedSpam):
    pass


class BadLogger2(CachedSpam):
    settings_uuid_field = "name"


class BadLogger3(CachedSpam):
    settings_uuid_field = "invalid_field"

    def __real_init__(self, *args, **kwargs): pass


def test_anti_pattern():
    with raises(RuntimeError):  # suggest to use .new()
        BadLogger1()

    with raises(NotImplementedError):  # suggest to implement klass.settings_uuid_field
        BadLogger1.new()

    with raises(RuntimeError):  # suggest to use .new()
        BadLogger2()

    with raises(NotImplementedError):  # suggest to implement def __real_init__(self, ...)
        BadLogger2.new(name="system")

    with raises(RuntimeError):  # suggest to use .new()
        BadLogger3()

    with raises(SyntaxError):  # suggest to use .new(invalid_field=xxx)
        BadLogger3.new(name="system")


class Logger(CachedSpam):
    settings_uuid_field = "name"

    def __real_init__(self, name):
        self.name = name

    def info(self, msg):
        pass


class Config(CachedSpam):
    settings_uuid_field = "name"

    def __real_init__(self, name):
        self.name = name


def test():
    with raises(RuntimeError):
        Logger("system")

    # logger1 = Logger.new("system")
    logger1 = Logger.new(name="system")
    logger2 = Logger.new(name="system")
    logger3 = Logger.new(name="user")
    assert logger1 is logger2
    assert logger1 is not logger3

    config1 = Config.new(name="system")
    config2 = Config.new(name="system")
    config3 = Config.new(name="user")
    assert config1 is config2
    assert config1 is not config3

    assert Logger._cache is not Config._cache
    assert isinstance(Logger._cache["system"], Logger)
    assert isinstance(Config._cache["system"], Config)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
