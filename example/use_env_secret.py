# -*- coding: utf-8 -*-

from pysecret import EnvSecret

env = EnvSecret() # by default, it load secret value from ~/.bash_pysecret
env.set("var1", "value1")
env.load_pysecret_script()
print(list(env.environ.keys()))
