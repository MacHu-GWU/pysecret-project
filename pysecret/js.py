# -*- coding: utf-8 -*-

import typing as T
import json
from pathlib import Path

from .js_helper import (
    create_json_if_not_exists,
    set_value,
    get_value,
    del_key,
    strip_comments,
)
from .singleton import CachedSpam

DEFAULT_JSON_SECRET_FILE = Path.home().joinpath(".pysecret.json")


class JsonSecret(CachedSpam):
    """
    Read and Write secret information from a JSON file.

    The secret content has to be a valid dictionary in JSON.
    """

    settings_uuid_field = "secret_file"

    def __real_init__(self, secret_file: Path = DEFAULT_JSON_SECRET_FILE):
        self.secret_file: Path = secret_file
        create_json_if_not_exists(str(self.secret_file))
        with open(self.secret_file, "rb") as f:
            self.data = json.loads(strip_comments(f.read().decode("utf-8")))

    def set(self, json_path: str, value) -> dict:
        self.data = set_value(self.data, json_path, value)
        self.secret_file.write_text(
            json.dumps(
                self.data,
                indent=4,
                ensure_ascii=False,
            )
        )
        return self.data

    def get(self, json_path: str) -> T.Any:
        return get_value(self.data, json_path)

    def unset(self, json_path: str):
        return del_key(self.data, json_path)
