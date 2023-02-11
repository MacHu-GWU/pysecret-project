# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from pysecret import path_bash_profile
from pysecret.tests import run_cov_test
from pysecret.sh import BaseShellScriptSecret


@dataclasses.dataclass
class Secret(BaseShellScriptSecret):
    PYENV_ROOT: T.Optional[str] = dataclasses.field(default=None)


def test():
    secret = Secret.load(str(path_bash_profile))
    assert secret.PYENV_ROOT == "$HOME/.pyenv"

    _ = secret.to_json()


if __name__ == "__main__":
    run_cov_test(__file__, "pysecret.sh", preview=False)
