# -*- coding: utf-8 -*-

from pysecret import EnvSecret

env = EnvSecret()
env.load_pysecret_script()
print(list(env.environ.keys()))
