Installation
============
The installation of this package relies on the `BuildOut <http://www.buildout.org>`_ system. By default, the command line sequence:

.. code-block:: sh

  $ python bootstrap.py
  $ bin/buildout

should download and install all requirements.
There are a few exceptions to that.


Required Packages
-----------------

Bob
...
To install Bob_, please visit http://www.idiap.ch/software/bob and follow the installation instructions.
Please verify that you have at least version 1.2.0 of Bob installed.
If you have installed Bob in a non-standard directory, please open the buildout.cfg_ file from the base directory and set the ``prefixes`` directory accordingly.


CSU face recognition resources
..............................
Due to the fact that the CSU toolkit needs to be patched to work with the FaceRecLib_, the setup is unfortunately slightly more complicated.
To be able to run the experiments based on the CSU toolkit, i.e., the LDA-IR algorithm, please download the `CSU Face Recognition Resources`_.
After unpacking the CSU toolkit, it needs to be patched.
For this reason, please follow the instructions:

1. Patch the CSU toolkit:

  .. code-block:: sh

    $ bin/buildout -c buildout-before-patch.cfg
    $ bin/patch_CSU.py [YOUR_CSU_SOURCE_DIRECTORY]

2. Update the buildout.cfg_ file by modifying the ``sources-dir =`` entry to point to the patched version of the CSU toolkit

  Make sure that you update your installation by **again** calling:

  .. code-block:: sh

    $ bin/buildout

.. note::
  The patch file is only valid for the current version of the CSU toolkit (last checked in December 2012).
  If you have another version, please see `Getting help`_.

.. note::
  At Idiap, you can also use the pre-patched version of the CSU toolkit.
  Just try:

  .. code-block:: sh

    $ bin/buildout -c buildout-idiap.cfg

  instead of downloading and patching the CSU toolkit.


Image Databases
...............
All experiments are run on external image databases.
We do not provide the images from the databases themselves.
Hence, please contact the database owners to obtain a copy of the images.
The two databases used in our experiments can be downloaded here:

- BANCA [``banca``]: http://www.ee.surrey.ac.uk/CVSSP/banca
- The Good, the Bad & the Ugly [``gbu``]: http://www.nist.gov/itl/iad/ig/focs.cfm

Important!
''''''''''
After downloading the databases, you will need to tell our software, where it can find them by changing the ``original_directory`` in the **configuration file** `xfacereclib/paper/BeFIT2012/configurations.py <file:../xfacereclib/paper/BeFIT2012/configurations.py>`_.
In rare cases, you might need to change the ``original_extension`` as well.
Please let all other configuration parameters unchanged as this might influence the face recognition experiments and, hence, the reproducibility of the results.

.. note::
  The GBU database uses the data from `MBGC-V1 <http://www.nist.gov/itl/iad/ig/mbgc.cfm>`_ of the American Institute of Standards and Technology (`NIST <http://www.nist.gov>`_).
  Please assure that you have the version V1 of the MBGC database.

  The directory structure of MBGC seems to have changed lately.
  We try to keep our GBU database interface up to date.
  If the directory structure of your copy of the MBGC does not coincide with ours, please read the documentation of the `xbob.db.gbu <http://pypi.python.org/pypi/xbob.db.gbu>`_ to update the database interface.


Verifying your installation
---------------------------
All of our packages use the nose tests framework to assess the correctness of its implementation.
To run the nose tests, simply call:

.. code-block:: sh

  $ bin/nosetests

This will execute all registered nose tests from this package and all of its dependent packages.
Please assure that all tests pass (some of the tests are skipped), so that the final result is similar to::

  ...

  Ran 77 tests in 216.657s

  OK (SKIP=17)

In case you don't see the last line and, hence, some tests do not pass, please report a new bug at http://github.com/bioidiap/xfacereclib.paper.BeFIT2012.


Getting help
------------
In case anything goes wrong, please feel free to open a new ticket in our GitHub_ page, or send an email to manuel.guenther@idiap.ch.

.. include:: links.rst

