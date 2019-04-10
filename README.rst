.. image:: https://readthedocs.org/projects/pysecret/badge/?version=latest
    :target: https://pysecret.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://travis-ci.org/MacHu-GWU/pysecret-project.svg?branch=master
    :target: https://travis-ci.org/MacHu-GWU/pysecret-project?branch=master

.. image:: https://codecov.io/gh/MacHu-GWU/pysecret-project/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/MacHu-GWU/pysecret-project

.. image:: https://img.shields.io/pypi/v/pysecret.svg
    :target: https://pypi.python.org/pypi/pysecret

.. image:: https://img.shields.io/pypi/l/pysecret.svg
    :target: https://pypi.python.org/pypi/pysecret

.. image:: https://img.shields.io/pypi/pyversions/pysecret.svg
    :target: https://pypi.python.org/pypi/pysecret

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/pysecret-project

------


.. image:: https://img.shields.io/badge/Link-Document-blue.svg
      :target: https://pysecret.readthedocs.io/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
      :target: https://pysecret.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
      :target: https://pysecret.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
      :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/pysecret-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
      :target: https://github.com/MacHu-GWU/pysecret-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
      :target: https://github.com/MacHu-GWU/pysecret-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://pypi.org/pypi/pysecret#files


Welcome to ``pysecret`` Documentation
==============================================================================

Documentation for ``pysecret``.



Load Data From Environment
------------------------------------------------------------------------------

**Use with command line / shell script**:

1. put secret infor in ``~/.bashrc_pysecret``

.. code-block:: bash

    # content of ~/.bashrc_pysecret
    export DB_SECRET_MYDB_HOST="123.456.789.000"
    export DB_SECRET_MYDB_USERNAME="username"
    export DB_SECRET_MYDB_PASSWORD="password"

2. add ``source ~/.bashrc_pysecret`` line to ``~/.bashrc`` / ``~/.bashrc_pysecret`` / ``~/.zshrc`` / ``~/.config/fish/config.fish``. Or just add it to ``~/.bashrc`` and ``source ~/.bashrc`` in other shell initialization scripts.



Usage:

    pysecret env set VAR "value" # add `export VAR="value"` to `~/.bashrc_pysecret`
    pysecret env apply .bashrc # add `source ~/.bashrc_pysecret` line to `~/.bashrc`
    pysecret env apply .bash_profile # add `source ~/.bashrc_pysecret` line to `~/.bash_profile`
    pysecret env open # open







Load Data From Json File
------------------------------------------------------------------------------

.. code-block:: python

    from pysecret import JsonSecret, get_home_path

    SECRET_FILE = get_home_path(".pysecret.json")
    js = JsonSecret.new(secret_file=SECRET_FILE)

    # construct / update secret json file
    js.set("mydb.host": "123.456.789.000")
    js.set("mydb.username": "username")
    js.set("mydb.password": "password")

or you can just create ``$HOME/.pysecret.json`` includes:

.. code-block:: python

    {
        "mydb": {
            "host": "123.456.789.000",
            "username": "username",
            "password": "password
        }
    }

**Load secret safely**:

.. code-block:: python

    host = js.get("mydb.host")
    username = js.get("mydb.username")
    password = js.get("mydb.password")



.. _install:

Install
------------------------------------------------------------------------------

``pysecret`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install pysecret

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pysecret