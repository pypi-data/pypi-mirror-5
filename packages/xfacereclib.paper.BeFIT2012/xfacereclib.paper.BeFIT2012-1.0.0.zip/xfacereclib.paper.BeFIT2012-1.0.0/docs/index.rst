.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Mon 13 Aug 2012 12:36:40 CEST

An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms
====================================================================================

This package provides the source code to run the experiments published in the paper `An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms <http://publications.idiap.ch/index.php/publications/show/2431>`_.
It relies on the FaceRecLib_ to execute all face recognition experiments.
Most of the face recognition algorithms are implemented in Bob_, while one of them is taken from the `CSU Face Recognition Resources`_.

.. note::
  Currently, this package only works in Unix-like environments and under MacOS.
  Due to limitations of the Bob_ library, MS Windows operating systems are not supported.
  We are working on a port of Bob_ for MS Windows, but it might take a while.


.. toctree::
   :maxdepth: 2

   installation
   experiments


.. include:: links.rst
