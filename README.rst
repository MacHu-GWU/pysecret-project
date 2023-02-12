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

.. image:: https://img.shields.io/pypi/dm/pysecret.svg

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


Welcome to ``pysecret`` Documentation
==============================================================================

.. contents::
    :class: this-will-duplicate-information-and-it-is-still-useful-here
    :local:

``pysecret`` is a library to ease your life dealing with secret information.

For example, **if you have a database connection information, so you should not include it in your source code**. ``pysecret`` is the library that provides several options to deploy or access your secret data securely.

**Features**

1. access secret in `Environment Variable <https://github.com/MacHu-GWU/pysecret-project/blob/master/examples/01-Environment-Variable.ipynb>`_.
2. access secret `in shell script <https://github.com/MacHu-GWU/pysecret-project/blob/master/examples/02-Shell-Script.ipynb>`_.
3. access secret `in json file from Python <https://github.com/MacHu-GWU/pysecret-project/blob/master/examples/03-JSON.ipynb>`_.
4. deploy your secret to `AWS Parameter Store <https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html>`_ and use it in your application code, see `AWS Parameter Store example <https://github.com/MacHu-GWU/pysecret-project/blob/master/examples/04-AWS-Parameter-Store.ipynb>`_.
5. deploy your secret to `AWS Secret Manager <https://aws.amazon.com/secrets-manager/>`_ and use it in your application code, see `AWS Secret Manager example <https://github.com/MacHu-GWU/pysecret-project/blob/master/examples/05-AWS-Secret-Manager.ipynb>`_.
6. use AWS Key Management Service to encrypt or decrypt your data, see `AWS KMS example <https://github.com/MacHu-GWU/pysecret-project/blob/master/examples/06-AWS-KMS.ipynb>`_.


Install
------------------------------------------------------------------------------

``pysecret`` is released on PyPI, so all you need is:

.. code-block:: console

    $ pip install pysecret

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade pysecret
