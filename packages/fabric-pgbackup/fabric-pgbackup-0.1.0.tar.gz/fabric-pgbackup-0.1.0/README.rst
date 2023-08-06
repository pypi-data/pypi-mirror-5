===============================
Fabric PostgreSQL Backup
===============================

.. image:: https://badge.fury.io/py/fabric-pgbackup.png
    :target: http://badge.fury.io/py/fabric-pgbackup

.. image:: https://travis-ci.org/zalew/fabric-pgbackup.png?branch=master
    :target: https://travis-ci.org/zalew/fabric-pgbackup

.. image:: https://pypip.in/d/fabric-pgbackup/badge.png
    :target: https://crate.io/packages/fabric-pgbackup?version=latest

PostgreSQL backup/restore utilities for Fabric

* PyPI: http://pypi.python.org/pypi/fabric-pgbackup/
* GitHub: https://github.com/zalew/fabric-pgbackup/
* BitBucket: https://bitbucket.org/zalew/fabric-pgbackup/

* Docs: http://fabric-pgbackup.rtfd.org
* Issues: https://github.com/zalew/fabric-pgbackup/issues
* License: MIT

Features
--------

* TODO

Install
--------

.. code-block:: shell

    pip install fabric-pgbackup

Usage
--------

.. code-block:: python

    # fabfile.py
    from fabric-pgbackup import *

.. code-block:: python

    # config

**Backup**

.. code-block:: shell

    fab pg_backup

**Restore**

.. code-block:: shell

    fab pg_restore

See more in docs: http://fabric-pgbackup.rtfd.org


