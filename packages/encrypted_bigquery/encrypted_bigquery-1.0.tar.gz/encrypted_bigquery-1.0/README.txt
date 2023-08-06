ebq - command-line encrypting client that accesses BigQuery service
Copyright 2013 Google Inc.
http://code.google.com/p/encrypted-bigquery-client/

This file includes instructions for installing and using the ebq command line
tool or client.

Installing and running ebq
=====================================

1. (If you already have Python and setuptools installed, skip to step 2.)
   a. Install Python 2.7 or newer.
        http://www.python.org/download/

   b. Install setuptools
        http://pypi.python.org/pypi/setuptools

      The linked page describes how to download and install setuptools for
      your Python distribution.

2. Install ebq. There are two methods, easy_install and by manual installation:

   a) easy_install

   To install via easy_install, just type:
     easy_install encrypted_bigquery

    -- OR --

   b) manual installation

     1. Get encrypted_bigquery-x.y.z archive from pypi and extract contents:
          tar -zxvf encrypted_bigquery-x.y.z.tar

     2. Change to the ebq directory:
          cd encrypted_bigquery-x.y.z

     3. Run the install script:
          python setup.py install [--install-scripts=target_installation_directory]

Running ebq from the command line
=====================================

1. Try out ebq by displaying a list of available commands. Type:
  target_installation_directory/ebq

2. To display help information about a particular command, type:
  target_installation_directory/ebq help command_name

Authorizing bq to access your BigQuery data
=====================================

Same as with bq command line tool.

Basic ebq tutorial
=====================================

A tutorial with sample data and load and query examples is available at:
    https://docs.google.com/file/d/0B-WB8hYCrhZ6cmxfWFpBci1lOVE/edit?usp=sharing

=====================================

