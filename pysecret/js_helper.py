# -*- coding: utf-8 -*-

import os
import re


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


def strip_comment_line_with_symbol(line, start): # pragma: no cover
    """
    Strip comments from line string.
    """
    parts = line.split(start)
    counts = [len(re.findall(r'(?:^|[^"\\]|(?:\\\\|\\")+)(")', part))
              for part in parts]
    total = 0
    for nr, count in enumerate(counts):
        total += count
        if total % 2 == 0:
            return start.join(parts[:nr + 1]).rstrip()
    else:  # pragma: no cover
        return line.rstrip()


def strip_comments(string, comment_symbols=frozenset(('#', '//'))): # pragma: no cover
    """
    Strip comments from json string.

    :param string: A string containing json with comments started by comment_symbols.
    :param comment_symbols: Iterable of symbols that start a line comment (default # or //).
    :return: The string with the comments removed.
    """
    lines = string.splitlines()
    for k in range(len(lines)):
        for symbol in comment_symbols:
            lines[k] = strip_comment_line_with_symbol(lines[k], start=symbol)
    return '\n'.join(lines)