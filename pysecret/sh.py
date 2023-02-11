# -*- coding: utf-8 -*-

import typing as T
import os
import json
import dataclasses
from pathlib import Path

from .sh_helper import load_var_value_from_shell_script


@dataclasses.dataclass
class BaseShellScriptSecret:
    """
    A base class for environment secrets data container.
    """

    @classmethod
    def load(cls, path_sh: str):
        data = load_var_value_from_shell_script(path_sh)
        kwargs = {f.name: data.get(f.name) for f in dataclasses.fields(cls)}
        return cls(**kwargs)

    def to_json(self, pretty: bool = True) -> str:
        kwargs = dict()
        if pretty:
            kwargs["indent"] = 4
        return json.dumps(dataclasses.asdict(self), **kwargs)
