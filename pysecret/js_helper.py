# -*- coding: utf-8 -*-

import typing as T
from pathlib import Path
from re import findall


def create_json_if_not_exists(path: str):
    """
    Create an empty json file if not exists
    """
    p = Path(path)
    if p.exists() is False:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{}")


def set_value(
    data: dict,
    json_path: str,
    value: T.Any,
) -> dict:
    """
    Set a field in dictionary data using JSON path syntax.

    :param data: the dictionary data
    :param json_path: the dot notation JSON path syntax, for example:
        ".key", ".key1.key2.key3"
    :param value: the changed data

    TODO: add array index support
    """
    if json_path.startswith("."):
        if json_path == ".":
            return value
        else:
            json_path = json_path[1:]

    paths = json_path.split(".")
    path_length = len(paths)
    dct = data
    for ind, key in enumerate(paths):
        if ind == (path_length - 1):
            dct[key] = value
        else:
            dct.setdefault(key, {})
            dct = dct[key]
    return data


def get_value(
    data: dict,
    json_path: str,
) -> T.Any:
    """
    Get the value of a field in dictionary data using JSON path syntax.

    :param data: the dictionary data
    :param json_path: the dot notation JSON path syntax, for example:

    TODO: add array index support
    """
    if json_path.startswith("."):
        if json_path == ".":
            return data
        else:
            json_path = json_path[1:]

    paths = json_path.split(".")
    value = data
    for key in paths:
        value = value[key]
    return value


def del_key(
    data: dict,
    json_path: str,
):
    """
    Delete a field in dictionary data using JSON path syntax.

    :param data: the dictionary data
    :param json_path: the dot notation JSON path syntax, for example:

    TODO: add array index support
    """
    paths = json_path.split(".")
    for key in paths[:-1]:
        data = data[key]
    del data[paths[-1]]


def strip_comment_line_with_symbol(
    line: str,
    comment_symbol: str,
) -> str:  # pragma: no cover
    """
    Strip comments from line string.

    :param line: the single line string that you want to strip out comments.
    :param comment_symbol: the comment char that indicate that the comment starts from.

    :return: the single line string with comment removed.
    """
    parts = line.split(comment_symbol)
    counts = [len(findall(r'(?:^|[^"\\]|(?:\\\\|\\")+)(")', part)) for part in parts]
    total = 0
    for nr, count in enumerate(counts):
        total += count
        if total % 2 == 0:
            return comment_symbol.join(parts[: nr + 1]).rstrip()
    else:  # pragma: no cover
        return line.rstrip()


def strip_comments(
    text: str,
    comment_symbols=frozenset(("#", "//")),
) -> str:  # pragma: no cover
    """
    Strip comments from json string.

    :param text: A string containing json with comments started by comment_symbols.
    :param comment_symbols: Iterable of symbols that start a line comment (default # or //).

    :return: the multi line text with the comments removed.
    """
    lines = text.splitlines()
    for k in range(len(lines)):
        for symbol in comment_symbols:
            lines[k] = strip_comment_line_with_symbol(lines[k], symbol)
    return "\n".join(lines)
