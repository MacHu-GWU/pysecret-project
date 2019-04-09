# -*- coding: utf-8 -*-


import weakref


class CachedSpamManager(object):
    """
    Instance cache manager.
    """
    cached_klass = None

    def __init__(self):
        self._cache = weakref.WeakValueDictionary()

    def new(self, name, *args, **kwargs):
        """
        Factory method.
        """
        if name not in self._cache:
            temp = self.cached_klass._new(name, *args, **kwargs)
            self._cache[name] = temp
        else:
            temp = self._cache[name]
        return temp

    def clear(self):
        self._cache.clear()


class Spam(object):
    def __init__(self, name, *args, **kwargs):
        msg = "Can't instantiate directly, use Cached{}Manager.new(name, ...) instead." \
            .format(self.__class__.__name__)
        raise RuntimeError(msg)

    # Alternate constructor
    @classmethod
    def _new(cls, name, *args, **kwargs):
        """
        User custom instance constructor.

        implement constructor this way::

            def _new(cls, name, *args, **kwargs):
                self = cls.__new__(cls)
                # put __init__(...) logic here
                self.name = name
                return self
        """
        raise NotImplementedError
