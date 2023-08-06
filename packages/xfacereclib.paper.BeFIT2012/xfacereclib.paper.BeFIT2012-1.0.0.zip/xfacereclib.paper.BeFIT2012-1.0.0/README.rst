An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms
====================================================================================

This package provides the source code to run the experiments published in the paper `An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms <http://publications.idiap.ch/index.php/publications/show/2431>`_.
It relies on the FaceRecLib_ to execute all face recognition experiments.
Most of the face recognition algorithms are implemented in Bob_, while one of them is taken from the `CSU Face Recognition Resources`_.

.. note::
  Currently, this package only works in Unix-like environments and under MacOS.
  Due to limitations of the Bob library, MS Windows operating systems are not supported.
  We are working on a port of Bob for MS Windows, but it might take a while.

.. note::
  The experiments described in this section use the FaceRecLib_ in version 1.1.3, Bob_ in version 1.2.0 and the January 2012 release of the `CSU Face Recognition Resources`_.
  These versions are pin-pointed in the **setup.py** file (see the ``install_requires`` section).
  For other versions, the results might be slightly different.

Installation
------------
The installation of this package relies on the BuildOut_ system. By default, the command line sequence::

  $ python bootstrap.py
  $ bin/buildout

should download and install most requirements, including the FaceRecLib_, the Database interface packages for the `BANCA database <http://pypi.python.org/pypi/xbob.db.banca>`_ and `the Good, the Bad & the Ugly database <http://pypi.python.org/pypi/xbob.db.gbu>`_, and, finally, the `Wrapper classes for the CSU Face Recognition Resources <http://pypi.python.org/pypi/xfacereclib.extension.CSU>`_.
Unfortunately, some packages must be installed manually:

Bob
...
To install the Bob toolkit, please visit http://www.idiap.ch/software/bob/ and follow the installation instructions.
Please verify that you have at least version 1.2.0 of Bob installed.
If you have installed Bob in a non-standard directory, please open the **buildout.cfg** file from the base directory and set the 'prefixes' directory accordingly.

CSU Face Recognition Resources
..............................
Due to the fact that the CSU toolkit needs to be patched to work with the FaceRecLib, the setup is unfortunately slightly more complicated.
To be able to run the experiments based on the CSU toolkit, i.e., the LDA-IR algorithm, please download the CSU Face Recognition Resources from http://www.cs.colostate.edu/facerec.
After unpacking the CSU toolkit, it needs to be patched.
For this reason, please follow the instructions:

1. Patch the CSU toolkit::

   $ bin/buildout -c buildout-before-patch.cfg
   $ bin/patch_CSU.py [YOUR_CSU_SOURCE_DIRECTORY]

2. Update the **buildout.cfg** file by modifying the ``sources-dir = [YOUR_CSU_SOURCE_DIRECTORY]`` entry to point to the base directory of the patched version of the CSU toolkit.

Make sure that you update your installation by **again** calling::

  $ bin/buildout

.. note::
  The patch file is only valid for the current version of the CSU toolkit (last checked in December 2012).
  If you have another version, please see the `Getting help`_ section.

.. note::
  At Idiap, you can also use the pre-patched version of the CSU toolkit.
  Just use::

    $ bin/buildout -c buildout-idiap.cfg

  instead of downloading and patching the CSU toolkit.


Databases
.........

Of course, we are not allowed to re-distribute the original images to run the experiments on.
To re-run the experiments, please make sure to have your own copy of the `BANCA <http://www.ee.surrey.ac.uk/CVSSP/banca>`_ and `the Good, the Bad & the Ugly <http://www.nist.gov/itl/iad/ig/focs.cfm>`_ images.


Documentation
-------------
After installing you might want to create the documentation for this satellite package, which includes more detailed information on how to re-run the experiments and regenerate the scientific plots from the paper.
To generate and open the documentation execute::

  $ bin/sphinx-build docs sphinx
  $ firefox sphinx/index.html

Of course, you can use any web browser of your choice.


Getting help
------------

In case anything goes wrong, please feel free to open a new ticket in our `GitHub page <https://github.com/bioidiap/xfacereclib.paper.BeFIT2012>`_, or send an email to manuel.guenther@idiap.ch.


Cite our paper
--------------

If you use the FaceRecLib_ or this package in any of your experiments, please cite the following paper::

  @inproceedings{Guenther_BeFIT2012,
         author = {G{\"u}nther, Manuel AND Wallace, Roy AND Marcel, S{\'e}bastien},
         editor = {Fusiello, Andrea AND Murino, Vittorio AND Cucchiara, Rita},
       keywords = {Biometrics, Face Recognition, Open Source, Reproducible Research},
          month = oct,
          title = {An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms},
      booktitle = {Computer Vision - ECCV 2012. Workshops and Demonstrations},
         series = {Lecture Notes in Computer Science},
         volume = {7585},
           year = {2012},
          pages = {547-556},
      publisher = {Springer Berlin},
       location = {Heidelberg},
            url = {http://publications.idiap.ch/downloads/papers/2012/Gunther_BEFIT2012_2012.pdf}
  }


.. _facereclib: http://pypi.python.org/pypi/facereclib
.. _bob: http://www.idiap.ch/software/bob
.. _csu face recognition resources: http://www.cs.colostate.edu/facerec
.. _buildout: http://www.buildout.org

