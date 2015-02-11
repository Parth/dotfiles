bq - command-line utilities to access BigQuery service
Copyright 2011 Google Inc.
http://code.google.com/p/google-bigquery-tools/

This file includes instructions for installing and using the bq command line
tool.

Installing and running bq
=====================================

1. (If you already have Python and setuptools installed, skip to step 2.)
   a. Install Python 2.6.5 or newer.
        http://www.python.org/download/

   b. Install setuptools
        http://pypi.python.org/pypi/setuptools

      The linked page describes how to download and install setuptools for
      your Python distribution.

2. Install bq. There are two methods, easy_install and by manual installation:

   a) easy_install

   To install via easy_install, just type:
     easy_install bigquery

   You can also directly install bq from:
     easy_install https://google-bigquery-tools.googlecode.com/files/bigquery-x.y.z.tar.gz [--script_dir target_installation_directory]

    -- OR --

   b) manual installation

     1. Extract contents of bigquery-x.y.z archive:
          tar -zxvf bigquery-x.y.z.tar

     2. Change to the bq directory:
          cd bigquery-x.y.z

     3. Run the install script:
          python setup.py install [--install-scripts=target_installation_directory]

Running bq from the command line
=====================================

1. Try out bq by displaying a list of available commands. Type:
  target_installation_directory/bq

2. To display help information about a particular command, type:
  target_installation_directory/bq help command_name

Authorizing bq to access your BigQuery data
=====================================

While the bq tool can be used without any setup, it is highly recommended
that you create and store authorization credentials to access your BigQuery
data. This can be done by using the 'bq init' command.

1. To create and store authorization credentials, type:
 target_installation_directory/bq init

2. This will provide a URL where you can authorize bq to act on your behalf
when accessing the BigQuery API. Visit this URL in a web browser, copy the
resulting code, and paste it on the command line when prompted by bq.

3. This step will store an OAuth token a file called ~/.bigquery.token, which
will remain valid until revoked by the user.

4. After authorizing bq, you will then be asked to choose a default BigQuery
project. This information will be stored in your home directory in the file
'.bigqueryrc'.

Basic bq commands
=====================================

Note: If you have not run "bq init" (see above) to store authorization
credentials, you will be asked to do before any operation involving data.

The following commands have additional options. For more information about
a specific command type:
  target_installation_directory/bq help command_name

1. You can run a query using the 'bq query' command:
  target_installation_directory/bq query 'select count(*) from
    publicdata:samples.shakespeare'

2. To list objects present in a collection, use 'bq ls':
  target_installation_directory/bq ls

3. Create a new table or dataset with 'bq mk':
  target_installation_directory/bq mk my_new_dataset

4. Load data from a source URI to a destination table with 'bq load':
  target_installation_directory/bq load <destination_table> <source_uri> <schema>

Running bq in shell mode
=====================================

1. bq can be run in an interactive shell mode. To enter shell mode, type:
  target_installation_directory/bq shell

2. In shell mode, you will be presented a command prompt, which will display
your default project GUID and dataset, if these values have been set. For
example:
  projectguid> help
  projectguid> ls
  projectguid> query 'select count(*) from publicdata:samples.shakespeare'
