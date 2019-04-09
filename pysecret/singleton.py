# -*- coding: utf-8 -*-

import weakref


class CachedSpam(object):
    """
    Cache instance with based on its' name.
    """
    settings_uuid_field = None

    _cache = None

    def __init__(self, *args, **kwargs):
        msg = "Can't instantiate directly, use {}._new(...) instead." \
            .format(self.__class__.__name__)
        raise RuntimeError(msg)

    def __real_init__(self, *args, **kwargs):
        msg = ("You have to implement ``def __real_init__(self, ...)`` "
               "like you implement ``def __init__(self, ...)``!")
        raise NotImplementedError(msg)

    @classmethod
    def _init_cache(cls):
        if cls._cache is None:
            cls._cache = weakref.WeakValueDictionary()

    @classmethod
    def new(cls, *args, **kwargs):
        cls._init_cache()
        if cls.settings_uuid_field is None:
            msg = "You have to specify `CachedSpam.settings_uuid_field`!"
            raise NotImplementedError(msg)
        if cls.settings_uuid_field not in kwargs:
            msg = "Can't find '{}' in {} Please use `CachedSpam.new({}=xxx)`".format(
                cls.settings_uuid_field, kwargs, cls.settings_uuid_field)
            raise SyntaxError(msg)
        uuid = kwargs[cls.settings_uuid_field]
        if uuid in cls._cache:
            return cls._cache[uuid]
        else:
            self = cls.__new__(cls)
            self.__real_init__(*args, **kwargs)
            cls._cache[uuid] = self
            return self
