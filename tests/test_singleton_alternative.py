# -*- coding: utf-8 -*-

import pytest
from pytest import raises
from pysecret.singleton_alternative import CachedSpamManager, Spam


class Logger(Spam):
    @classmethod
    def _new(cls, name, *args, **kwargs):
        self = cls.__new__(cls)
        self.name = name
        return self

    def info(self, msg): pass


class CachedLoggerManager(CachedSpamManager):
    cached_klass = Logger


logger_manager = CachedLoggerManager()


class Config(Spam):
    @classmethod
    def _new(cls, name, *args, **kwargs):
        self = cls.__new__(cls)
        self.name = name
        return self

    def info(self, msg): pass


class CachedConfigManager(CachedSpamManager):
    cached_klass = Config


config_manager = CachedConfigManager()


def test():
    with raises(RuntimeError):
        Logger("system")

    logger1 = logger_manager.new("system")
    logger2 = logger_manager.new("system")
    logger3 = logger_manager.new("user")
    assert logger1 is logger2
    assert logger1 is not logger3

    config1 = config_manager.new("system")
    config2 = config_manager.new("system")
    config3 = config_manager.new("user")
    assert config1 is config2
    assert config1 is not config3

    assert logger_manager._cache is not config_manager._cache
    assert isinstance(logger_manager._cache["system"], Logger)
    assert isinstance(config_manager._cache["system"], Config)

    logger_manager.clear()


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
