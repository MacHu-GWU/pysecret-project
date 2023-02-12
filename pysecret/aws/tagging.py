# -*- coding: utf-8 -*-

import typing as T


def encode_tags(tags: T.Dict[str, str]) -> T.List[T.Dict[str, str]]:
    return [{"Key": key, "Value": value} for key, value in tags.items()]


def decode_tags(tag_list: T.List[T.Dict[str, str]]) -> T.Dict[str, str]:
    return {dct["Key"]: dct["Value"] for dct in tag_list}
