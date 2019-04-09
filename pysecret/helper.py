# -*- coding: utf-8 -*-

import os

HOME = os.path.expanduser("~")


def append_line_if_not_exists(path, line):
    if not os.path.exists(path):
        return
    
    striped_line = line.strip()
    with open(path, "rb") as f:
        content = f.read().decode("utf-8")
        flag_endswith_new_line = content.endswith("\n") or content.endswith("\n\r")
        for line_ in content.split("\n"):
            if striped_line in line_:
                return

    with open(path, "ab") as f:
        if flag_endswith_new_line:
            f.write((line + "\n").encode("utf-8"))
        else:
            f.write(("\n" + line + "\n").encode("utf-8"))


def set_env_var(var, value):
    os.environ[var] = str(value)
