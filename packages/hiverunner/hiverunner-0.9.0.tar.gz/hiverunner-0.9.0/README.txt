===========
Hive Runner
===========

Hive Runner is a python script that pulls saved queries from Beeswax, runs the
queries on Hive, and stores the results in Memcache.

Using Hive Runner
=================

Requirements
------------

* Cloudera Beeswax - Beeswax must be using a MySQL Database for storage.
* HiveServer - You must be running HiveServer version 1. Note that Cloudera’s
  Hadoop distribution only ships with version 2. You can easily install version
  1 using Cloudera’s package repositories.
* Memcached - You must have Memcached running somewhere.
* Pip - Pip is used for Python package dependency.

Installation
------------

* Optionally, create a VirtualEnv: ``virtualenv environment-name``
* Optionally, use your VirtualEnv: ``source environment-name/bin/activate``
* Install Hive Run via pip: ``pip install hiverunner``

Usage
-----

Hive Runner has many parameters. Example::
    python hiverunner.py --hourly \
    --mysql-host mysql01.example.com --mysql-database beeswax \
    --mysql-user hue --mysql-password secret \
    --hive-host hive01.example.com \
    --memcache-host cache01.example.com

Contributors
============
Kevin Reedy <kevin@bellycard.com>
AJ Self <aj@bellycard.com>

License
=======
Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
