# -*- coding: utf-8 -*-


import os
import re

export_pattern = re.compile('export [a-zA-Z0-9_]{1,128}="[a-zA-Z0-9_]{1,128}"')

s = """
export VAR="value"
export USERNAME="alice"
"""
for line in s.split("\n"):
    line = line.strip()
    print(re.findall(export_pattern, line))


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


def load_env_var(shell_scripts):
    with open(shell_scripts, "rb") as f:
        candidates = list()
        lines = f.read().decode("utf-8")
        for line in lines.split("\n"):
            line = line.strip()
            for item in re.findall(export_pattern, line):
                candidates.append(item)
        results = dict()
        for item in candidates:
            if item.startswith("export ") and ('="' in item) and item.endswith('"'):
                item = item[7:]
                print(item)

print(load_env_var(""))