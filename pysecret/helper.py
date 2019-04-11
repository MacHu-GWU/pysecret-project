# -*- coding: utf-8 -*-

import os

HOME = os.path.expanduser("~")


def home_file_path(*args):  # pragma: no cover
    return os.path.join(HOME, *args)
