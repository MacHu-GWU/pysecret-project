# -*- coding: utf-8 -*-

import os
from superjson import json
from .helper import HOME
from .singleton import CachedSpam
from .js_helper import create_json_if_not_exists, set_value, get_value, del_key

DEFAULT_JSON_SECRET_FILE = os.path.join(HOME, ".pysecret.json")


class JsonSecret(CachedSpam):
    """

    """
    settings_uuid_field = "secret_file"

    def __real_init__(self, secret_file=DEFAULT_JSON_SECRET_FILE):
        self.secret_file = secret_file
        create_json_if_not_exists(self.secret_file)
        with open(self.secret_file, "rb") as f:
            self.data = json.loads(f.read().decode("utf-8"))

    def set(self, json_path, value):
        set_value(self.data, json_path, value)
        json.dump(self.data, self.secret_file,
                  pretty=True, ensure_ascii=False, overwrite=True, verbose=False)

    def get(self, json_path):
        return get_value(self.data, json_path)


    def unset(self, json_path):
        return del_key(self.data, json_path)
