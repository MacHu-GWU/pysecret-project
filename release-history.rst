.. _release_history:

Release and Version History
==============================================================================


1.0.4 (TODO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


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

- Stablize API


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
