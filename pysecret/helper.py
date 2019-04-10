# -*- coding: utf-8 -*-

import os

HOME = os.path.expanduser("~")


def home_file_path(*args):
    return os.path.join(HOME, *args)


def set_env_var(var, value):
    os.environ[var] = str(value)
