# -*- coding: utf-8 -*-

import typing as T


def ensure_only_one_true(kv_list: T.List[T.Tuple[str, bool]]):
    if sum([v for _, v in kv_list]) != 1:
        raise ValueError(
            "one and only one argument in {} has to be True!".format(
                ", ".join([f"{k!r}" for k, _ in kv_list])
            )
        )
