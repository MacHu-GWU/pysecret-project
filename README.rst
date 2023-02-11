.. image:: https://readthedocs.org/projects/pysecret/badge/?version=latest
    :target: https://pysecret.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/pysecret-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/pysecret-project/actions?query=workflow:CI

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

.. image:: https://img.shields.io/badge/Link-Document-green.svg
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

.. contents::
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:

``pysecret`` is a library to ease your life dealing with secret information.

For example, **if you have a database connection information, so you should not include it in your source code**. ``pysecret`` is the library that provides several options to deploy or access your secret data securely:

**Features**:

1. access secret in Environment Variable.
2. access secret in shell script.
3. access secret in json file from Python.
4. use AWS Key Management Service to encrypt or decrypt your data.
5. deploy your secret to AWS Parameter Store and use it in your application code.
6. deploy your secret to AWS Secret Manager and use it in your application code.


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

**Encrypt your secret and Read secret value using AWS Secret Manager with ``pysecret`` is super easy**.

First, let's create a aws secret:

.. code-block:: python

    from pysecret import AWSSecret

    aws_profile = "my_aws_profile"
    aws = AWSSecret(profile_name=aws_profile)

    secret_id = "my-example-secret"
    secret_data = dict(
        host="www.example.com",
        port=1234,
        database="mydatabase",
        username="admin",
        password="mypassword",
        metadata=dict(
            creator="Alice",
        )
    )
    aws.deploy_secret(name=secret_id, secret_data=secret_data)

Now open your AWS Console https://console.aws.amazon.com/secretsmanager/home?region=us-east-1#/secret?name=my-example-secret (Replace us-east-1 to your region), you should be able to see the new AWS Secret has been created.

Now let's retrive the secret value

.. code-block:: python

    >>> aws.get_secret_value(secret_id="my-example-secret", key="password")
    mypassword
    >>> aws.get_secret_value(secret_id="my-example-secret", key="metadata.creator")
    Alice

**Use KMS Key to encrypt and decrypt text is easy**

.. code-block:: python

    >>> from pysecret import AWSSecret
    >>> aws_profile = "my_aws_profile"
    >>> kms_key_id = "abcd1234-ab12-ab12-ab12-abcd1234abcd"

    >>> aws = AWSSecret(profile_name=aws_profile)
    >>> secret = "Hello World".encode("utf-8)
    >>> encrypted_blob = aws.kms_encrypt(kms_key_id, secret)
    >>> decrypted_blob = aws.kms_decrypt(encrypted_blob)
    >>> assert secret != encrypted_blob
    True
    >>> assert secret == decrypted_blob
    True
    >>> decrypted_blob.decode("utf-8")
    Hello World


AWS System Manager Parameter Store Integration
------------------------------------------------------------------------------

**Parameter store is a Free service allows you to securely store parameters**

First let's create a parameter:

.. code-block:: python

    from pysecret import AWSSecret

    aws_profile = "my_aws_profile"
    aws = AWSSecret(profile_name=aws_profile)


    parameter_name = "my-example-parameter"
    parameter_data = dict(
        project_name="my-example-project",
        metadata=dict(
            creator="Alice",
        ),
    )

    aws.deploy_parameter(
        name=parameter_name,
        parameter_data=parameter_data,
        use_default_kms_key=True, # encrypt it with default kms key
    )

Now open your AWS Console https://console.aws.amazon.com/systems-manager/parameters/my-example-parameter/description?region=us-east-1 (Replace us-east-1 to your region), you should be able to see the new Parameter has been created.

Now let's retrive the parameter value:

.. code-block:: python

    # read parameter from AWS
    assert aws.get_parameter_value(parameter_name, "project_name") == parameter_data["project_name"]
    assert aws.get_parameter_value(parameter_name, "metadata.creator") == parameter_data["metadata"]["creator"]

It also **support complex parameter object TOO**, with ``attrs`` python library:

.. code-block:: python

    import attr

    @attr.s
    class Credential:
        username = attr.ib()
        password = attr.ib()

    @attr.s
    class PasswordBook:
        amazon = attr.ib()
        google = attr.ib()
        facebook = attr.ib()

    password_book = PasswordBook(
        amazon=Credential("alice@amazon.com", "amazonpassword"),
        google=Credential("alice@google.com", "googlepassword"),
        facebook=Credential("alice@facebook.com", "facebookpassword"),
    )

    parameter_name = "my-passwordbook"

    aws.deploy_parameter_object(
        name=parameter_name,
        parameter_obj=password_book,
        use_default_kms_key=True, # encrypt it with default kms key
    )

Then you can read complex object from parameter store:

.. code-block:: python

    password_book = aws.get_parameter_object(name=parameter_name)
    print(password_book.facebook.password) # should be "facebookpassword"


.. _install:

Install
------------------------------------------------------------------------------

``pysecret`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install pysecret

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pysecret
