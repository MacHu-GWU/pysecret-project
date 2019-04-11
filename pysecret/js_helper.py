# -*- coding: utf-8 -*-

import os


def create_json_if_not_exists(path):  # pragma: no cover
    if not os.path.exists(path):
        with open(path, "wb") as f:
            f.write("{}".encode("utf-8"))


def set_value(data, json_path, value):
    paths = json_path.split(".")
    path_length = len(paths)
    for ind, key in enumerate(paths):
        if ind == (path_length - 1):
            data[key] = value
        else:
            data.setdefault(key, {})
            data = data[key]
    return data


def get_value(data, json_path):
    paths = json_path.split(".")
    value = data
    for key in paths:
        value = value[key]
    return value


def del_key(data, json_path):
    paths = json_path.split(".")
    for key in paths[:-1]:
        data = data[key]
    del data[paths[-1]]
