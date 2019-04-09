# -*- coding: utf-8 -*-

import weakref


class CachedSpam(object):
    """
    Cache instance with based on its' name.
    """
    _cache = None

    def __init__(self, name, *args, **kwargs):
        msg = "Can't instantiate directly, use {}._new(...) instead." \
            .format(self.__class__.__name__)
        raise RuntimeError(msg)

    def __real_init__(self, name, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def _init_cache(cls):
        if cls._cache is None:
            cls._cache = weakref.WeakValueDictionary()

    @classmethod
    def new(cls, name, *args, **kwargs):
        cls._init_cache()
        if name in cls._cache:
            return cls._cache[name]
        else:
            self = cls.__new__(cls)
            self.__real_init__(name, *args, **kwargs)
            cls._cache[name] = self
            return self
