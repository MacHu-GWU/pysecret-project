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

``pysecret`` is a library to ease your life dealing with secret information.

For example, **if you have a database connection information, so you can't include it in your source code, but you want to easily and securely access it**, then ``pysecret`` is the library for you. It provides several options out of the box:

**Features**:

1. access secret in environment variable from commandline, shell scripts, or Python.
2. access secret in json file from Python.
3. use AWS Key Management Service or AWS Secret Manager to access your secret info.

For large file or binary data encryption, I highly recommend you to use AWS Key Management Service and AWS Secret Manager to fetch your encryption key, then use `windtalker <https://pypi.org/project/windtalker/>`_ library to encrypt it.



Load Data From Environment
------------------------------------------------------------------------------

The idea is: put your secret information in ``~/.bashrc_pysecret`` file.

.. code-block:: bash

    # content of ~/.bashrc_pysecret file
    export DB_SECRET_MY_DB_PASSWORD="mypassword"
    ...

And put ``source ~/.bashrc_pysecret`` into your ``~/.bashrc`` / ``~/.bash_profile`` / ``.zshrc`` ...

**Whenever you need your secret info**:

1. Your interactive command line interface gives you easy access to those secrets.
2. You can put ``source ~/.bashrc_pysecret`` in your CI / CD scripts.
3. pysecret allows you to load secret value in python code. By doing this:

.. code-block:: python

    >>> from pysecret import EnvSecret
    >>> env = EnvSecret()
    >>> env.load_pysecret_script()
    >>> env.get("DB_SECRET_MY_DB_PASSWORD")
    mypassword

**You can write your secret to** ``~/.bashrc_pysecret`` **file in a pythonic way**:

.. code-block:: python

    from pysecret import EnvSecret

    env = EnvSecret()

    # will create ~/.bashrc_pysecret file if not exists
    # will update ~/.bashrc_pysecret file too
    # if you don't want to update ~/.bashrc_pysecret file, just set .set(..., temp=True)
    env.set("DB_SECRET_MYDB_HOST", "123.456.789.000")
    env.set("DB_SECRET_MYDB_USERNAME", "username")
    env.set("DB_SECRET_MYDB_PASSWORD", "password")


Load Data From Json File
------------------------------------------------------------------------------

The idea is, put your secret info in a json file and load info from it. You can create it manually by your own, or do it in pythonic way:

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


AWS Key Management Service and Secret Manager Integration
------------------------------------------------------------------------------

Create a encryption key in AWS KMS, then encrypt your secret info with the key in AWS Secret Manger. Access it is easy with ``pysecret``.

Suppose you defined a "secret" called "my-secret" in AWS Secret Manger:

- username: "myusername"
- password: "mypassword"


.. code-block:: python

    >>> from pysecret import AWSSecret

    >>> aws_profile = "my_aws_profile"
    >>> aws = AWSSecret(profile_name=aws_profile)
    >>> aws.get_secret_value(secret_id="my-secret", key="password")
    mypassword


.. _install:

Install
------------------------------------------------------------------------------

``pysecret`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install pysecret

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pysecret