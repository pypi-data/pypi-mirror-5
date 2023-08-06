=======
SiQueries
=======

SiQueries utilities for providing read-only user local database access.

Version 1.0.8


Introduction
------------
This util permits SiQueries customers to provide database access by
opening an SSH reverse tunnel from a SiQueries server to the customer
database.

Errors, comments, questions may be sent to support[at]siqueries[dot]com.


Requirements
------------
Requires a read-only database role (or authorization to create one)
and a local SSH client.

Supported Databases
-------------------
MySQL
PostgreSQL


Installation
------------
To install, type::

    $ python setup.py install

To uninstall, remove the files
    siqueries_install
    siqueries_connect


Troubleshooting
-------------
If you encounter an error while running siqueries_install, the file
    /tmp/siqueries_error_log.html
may contain details on what went wrong. In any event, please feel free
to contact support.


Documentation
-------------
Further documentation may be found at http://siqueries.com/


Package Contents
----------------
    siqueries_install
        The configuration wizard

    siqueries_connect
        A script to keep the SSH tunnel alive

Changes
-------
-Package fixed siqueries_install
