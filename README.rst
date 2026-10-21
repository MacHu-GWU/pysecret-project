.. image:: https://readthedocs.org/projects/pysecret/badge/?version=latest
    :target: https://pysecret.readthedocs.io/index.html
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/pysecret-project/workflows/CI/badge.svg
    :target: https://github.com/MacHu-GWU/pysecret-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/pysecret-project/branch/main/graph/badge.svg
  :target: https://codecov.io/gh/MacHu-GWU/pysecret-project

.. image:: https://img.shields.io/pypi/v/pysecret.svg
    :target: https://pypi.python.org/pypi/pysecret

.. image:: https://img.shields.io/pypi/l/pysecret.svg
    :target: https://pypi.python.org/pypi/pysecret

.. image:: https://img.shields.io/pypi/pyversions/pysecret.svg
    :target: https://pypi.python.org/pypi/pysecret

.. image:: https://img.shields.io/pypi/dm/pysecret.svg

.. image:: https://img.shields.io/badge/Release_History!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/pysecret-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/STAR_Me_on_GitHub!--None.svg?style=social
    :target: https://github.com/MacHu-GWU/pysecret-project


------

.. image:: https://img.shields.io/badge/Link-Document-green.svg
      :target: https://pysecret.readthedocs.io/index.html

.. image:: https://img.shields.io/badge/Link-API-blue.svg
      :target: https://pysecret.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Source_Code-blue.svg
      :target: https://pysecret.readthedocs.io/py-modindex.html

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
      :target: https://github.com/MacHu-GWU/pysecret-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
      :target: https://github.com/MacHu-GWU/pysecret-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
      :target: https://github.com/MacHu-GWU/pysecret-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
      :target: https://pypi.org/pypi/pysecret#files


Project Status: No Longer Maintained
==============================================================================

``pysecret`` is no longer maintained. Version 2.2.4 is the last release. It stays on PyPI and still installs, but it will get no bug fixes, no new features, and no support for new Python versions.

**Why**

``pysecret`` tried to do two jobs at once: store and load secrets, and serialize them (dict, list, and arbitrary Python objects through ``jsonpickle``). Serialization is the caller's job, and loading arbitrary objects with ``jsonpickle`` from a shared secret store can run arbitrary code. Once serialization is taken out, what is left is either something the standard library or a well-known package already does better (environment variables, ``.env``-style shell files, a local JSON file), or a thin wrapper around boto3 (AWS Parameter Store, Secrets Manager, KMS) that adds little over calling boto3 directly. There is no core feature left that justifies a separate library.

**What to use instead**

.. list-table::
    :header-rows: 1

    * - ``pysecret`` feature
      - Use instead
    * - ``BaseEnvVar``, ``AWSEnvVar``: load environment variables into a dataclass
      - ``os.environ``, or `pydantic-settings <https://pypi.org/project/pydantic-settings/>`_ for typed settings
    * - ``BaseShellScriptSecret``: read ``export KEY="value"`` lines from a shell script
      - `python-dotenv <https://pypi.org/project/python-dotenv/>`_
    * - ``JsonSecret``: local secrets in ``~/.pysecret.json``
      - `home-secret-toml <https://github.com/MacHu-GWU/home_secret_toml-project>`_
    * - AWS Parameter Store (``Parameter``, ``deploy_parameter``, ``delete_parameter``, parameter tags)
      - `simple_aws_ssm_parameter_store <https://github.com/MacHu-GWU/simple_aws_ssm_parameter_store-project>`_, which also writes a new version only when something changed
    * - AWS Secrets Manager (``Secret``, ``deploy_secret``, ``delete_secret``)
      - boto3's `Secrets Manager client <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html>`_
    * - AWS KMS (``kms_symmetric_encrypt``, ``kms_symmetric_decrypt``)
      - boto3's `KMS client <https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/kms.html>`_ (``encrypt`` and ``decrypt``)

The rest of this page documents version 2.2.4 as it was.


Welcome to ``pysecret`` Documentation
==============================================================================

.. contents::
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:

``pysecret`` is a library to ease your life dealing with secret information.

For example, **if you have a database connection information, so you should not include it in your source code**. ``pysecret`` is the library that provides several options to deploy or access your secret data securely.

**Features**

1. access secret in `Environment Variable <https://github.com/MacHu-GWU/pysecret-project/blob/main/examples/01-Environment-Variable.ipynb>`_.
2. access secret `in shell script <https://github.com/MacHu-GWU/pysecret-project/blob/main/examples/02-Shell-Script.ipynb>`_.
3. access secret `in json file from Python <https://github.com/MacHu-GWU/pysecret-project/blob/main/examples/03-JSON.ipynb>`_.
4. deploy your secret to `AWS Parameter Store <https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html>`_ and use it in your application code, see `AWS Parameter Store example <https://github.com/MacHu-GWU/pysecret-project/blob/main/examples/04-AWS-Parameter-Store.ipynb>`_.
5. deploy your secret to `AWS Secret Manager <https://aws.amazon.com/secrets-manager/>`_ and use it in your application code, see `AWS Secret Manager example <https://github.com/MacHu-GWU/pysecret-project/blob/main/examples/05-AWS-Secret-Manager.ipynb>`_.
6. use AWS Key Management Service to encrypt or decrypt your data, see `AWS KMS example <https://github.com/MacHu-GWU/pysecret-project/blob/main/examples/06-AWS-KMS.ipynb>`_.


Install
------------------------------------------------------------------------------

``pysecret`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install pysecret

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pysecret
