# -*- coding: utf-8 -*-

from pysecret import JsonSecret, DEFAULT_JSON_SECRET_FILE

js = JsonSecret.new(secret_file=DEFAULT_JSON_SECRET_FILE)
js.set("mydb.host", "localhost")
js.set("mydb.username", "username")
js.set("mydb.password", "password")

js = JsonSecret.new(secret_file=DEFAULT_JSON_SECRET_FILE)
print(js.get("mydb.host"))
print(js.get("mydb.username"))
print(js.get("mydb.password"))
