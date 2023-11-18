.. _release_history:

Release and Version History
==============================================================================


2.3.1 (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


2.2.4 (2023-11-18)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- fix a bug that when load AWS SSM parameter using label, the returned Parameter object doesn't have the correct label information.

**Miscellaneous**

- improved the documentation in the ``04-AWS-Parameter-Store.ipynb`` notebook.


2.2.3 (2023-05-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- fix a bug that sometime certain attributes are not available in AWS Parameter and Secret object.


2.2.2 (2023-02-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- fix a bug that ``pysecret.deploy_parameter`` should not use ``tags`` and ``overwrite`` together when creating a new parameter.


2.2.1 (2023-02-12)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add the following method to public API:
    - ``pysecret.get_parameter_tags``
    - ``pysecret.update_parameter_tags``
    - ``pysecret.put_parameter_tags``
    - ``pysecret.remove_parameter_tags``
- now ``pysecret.deploy_parameter`` allow full tags replacement and deletion.
- add ``version`` and ``label`` arguments to ``pysecret.Parameter.load(...)``.
- add ``pysecret.Parameter.put_label(...)``.
- add ``pysecret.Parameter.delete_label(...)``.


2.1.1 (2023-02-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Breaking Change**

- Redesigned the api. 2.X will not compatible to 1.X at all
- drop support for Python3.6, only supports for Python3.7+

**Features and Improvements**

- Below is the list of stabled API for 2.X:
    - ``pysecret.BaseEnvVar``: manage secrets in environment variables
    - ``pysecret.AWSEnvVar``: manage AWS CLI related secrets in environment variables
    - ``pysecret.JsonSecret``: manage secrets in JSON file
    - ``pysecret.BaseShellScriptSecret``: manage secrets in shell script
    - ``pysecret.Parameter``: manage secrets in AWS Parameter Store
    - ``pysecret.deploy_parameter``: manage secrets in AWS Parameter Store
    - ``pysecret.delete_parameter``: manage secrets in AWS Parameter Store
    - ``pysecret.Secret``: manage secrets in AWS Secret Manager
    - ``pysecret.deploy_secret``: manage secrets in AWS Secret Manager
    - ``pysecret.delete_secret``: manage secrets in AWS Secret Manager
    - ``pysecret.kms_symmetric_encrypt``: encrypt data using AWS KMS
    - ``pysecret.kms_symmetric_decrypt``: decrypt data using AWS KMS

**Minor Improvements**

- add jupyter notebook examples.


1.0.4 (2023-02-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- :meth:`pysecret.aws.AWSSecret.deploy_parameter`` and :meth:`pysecret.aws.AWSSecret.deploy_parameter_object`` now support ``skip_duplicate`` argument, so it won't deploy a new version when the content of the parameter is the same.


1.0.3 (2022-08-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add :meth:`pysecret.aws.AWSSecret.get_parameter_raw_value`` method
- add :meth:`pysecret.aws.AWSSecret.get_secret_raw_value`` method


1.0.2 (2022-03-26)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add :meth:`pysecret.aws.AWSSecret.delete_parameter`` method
- add :meth:`pysecret.aws.AWSSecret.delete_secret`` method

**Miscellaneous**

- update ``readthedocs.yml``


1.0.1 (2021-11-24)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Allow creating ``AWSSecret`` object with a pre-defined boto session object

**Miscellaneous**

- Stabilize API


0.0.9 (2021-10-07)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- allow dump complex object to AWS parameter store and AWS secret manager using ``attrs`` python library
- add three ``update_mode`` option for AWS deployment. ``create``, ``upsert``, ``try_create``.

**Minor Improvements**

- host doc site on readthedocs.org

**Bugfixes**

**Miscellaneous**

- Drop Python2.7 support, only support Python3.6+


0.0.8 (2020-04-18)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Bugfixes**

- ``tags`` arg should be ignored in ``pysecret.aws.AWSSecret.deploy_secret()`` method


0.0.7 (2020-04-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- allow to load secret from json with comments.


0.0.6 (2020-04-01)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- allow get value from KMS encrypted AWS paramter store.


0.0.5 (2020-02-27)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add AWS Parameter store support


0.0.4 (2019-10-11)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- add ``pysecret.AWSSecret.deploy_secret()`` method to allow developer to create and update secret easily.
- add json path support to ``pysecret.AWSSecret.get_secret_value()``

**Minor Improvements**

- improved AWSSercret document.


0.0.3 (2019-05-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Bugfixes**

- Fix a fatal bug that boto session are not used correctly

**Miscellaneous**

- add more type hint


0.0.2 (2019-04-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

1. access from environment variable
2. access from json file
3. integrate AWS KMS and AWS Secret Manager


0.0.1 (2019-04-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- First release
