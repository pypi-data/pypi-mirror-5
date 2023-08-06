Recreating the results
======================

After successfully setting up the databases, you are now able to re-run the face recognition experiments.
All experiment are run using the FaceRecLib_, but for convenience there exist wrapper scripts that set up the right parametrization for the call to the FaceRecLib_.
These scripts are ``bin/befit2012_execute.py`` and ``bin/befit2012_evaluate.py``.


Running the experiments
-----------------------
The former script is used to run all experiments.
The script requires some command line options, which you can list using ``bin/befit2012_execute.py --help``.
Usually, the command line options have a long version (starting with ``--``) and a shortcut (starting with a single ``-``), here we use only the long versions:

- ``--temp-directory`` (required): Specify a directory where temporary files will be stored. This directory can be deleted after all experiments ran successfully.
- ``--result-directory`` (required): Specify a directory where final result files will be stored. This directory is required to evaluate the experiments.
- ``--algorithms``: Specify a list of algorithms that you want to run. Possible values are: ``Graphs``, ``LGBPHS``, ``LDA-IR`` and ``ISV``. By default, all algorithms are run.
- ``--databases``: Specify a list of databases that you want your experiments to run on. Possible values are ``BANCA`` and ``GBU``. By default, experiments on both databases are executed.
- ``--verbose``: Print out additional information or debug information during the execution of the experiments. The ``--verbose`` option can be used several times, increasing the level to Warning (1), Info (2), Debug (3). By default, only Error (0) messages are printed.
- ``--grid``: Run the experiments in the SGE grid. Currently, this option is only available at Idiap_, but you can adapt the `SGE grid toolkit`_ towards your needs if required.
- ``--local``: Run the experiments using the given number of parallel threads on the local machine. You can monitor the execution of the jobs using the `SGE grid toolkit`_.
- ``--dry-run``: Use this option to print the calls to the FaceRecLib_ without executing them.

If neither ``--grid`` no ``--local`` is specified, the jobs will simply run in sequence on the local machine, using a single thread.

.. warning::
  The execution of the script may take a long time and require large amounts of memory.
  Specifically, when experiments are run in sequence, the execution of all experiments might take several days.

Additionally, you can pass options directly to the FaceRecLib_, but you should do that with care.
Simply use ``--`` to separate options to the ``bin/befit2012_execute.py`` from options to the FaceRecLib_.

It is advisable to use the ``--dry-run`` option before actually running the experiments, just to see that everything is correct.
Also, the Info (2) verbosity level prints useful information, e.g., by adding the ``--verbose --verbose`` (or shortly ``-vv``) on the command line.
A commonly used command line to execute all algorithms with on both databases could be one of:

1. Run the code in sequence on the local machine:

  .. code-block:: sh

    $ bin/befit2012_execute.py --result-directory [results] --temp-directory [temp] -vv

2. Run the code in parallel on the local machine using parallel processes (the number of processes can be adapted in the ``grid_local`` object at the `xfacereclib/paper/BeFIT2012/configurations.py <file:../xfacereclib/paper/BeFIT2012/configurations.py>`_ file:

  .. code-block:: sh

    $ bin/befit2012_execute.py --result-directory [results] --temp-directory [temp] -vv --local

  .. note::
    The script for running jobs in parallel on the local machine is in BETA status and might not work perfectly under all conditions.

3. Run the code in parallel in the SGE grid:

  .. code-block:: sh

    $ bin/befit2012_execute.py --result-directory [results] --temp-directory [temp] -vv --grid

  .. note::
    The grid configuration is adapted to run in the Idiap_ SGE grid.
    No other SGE grid has been tested so far, but in principle it should work fine.
    Maybe, a the grid configuration (i.e. the ``grid_simple`` and the ``grid_demanding`` objects) needs to be modified to work with your SGE grid.
    Please check the documentation of the FaceRecLib_ for details.


Evaluating the experiments
--------------------------
The second script can be used to evaluate the results generated with the first script.
Again, some command line parameters can be specified, see ``bin/befit2012_evaluate.py --help``:

- ``--result-directory`` (required): Specify the directory where final result files are stored. This should be the same directory as passed to the `bin/befit2012_execute.py`` script.
- ``--algorithms``: Specify a list of algorithms that you want to evaluate. Possible values are: ``Graphs``, ``LGBPHS``, ``LDA-IR`` and ``ISV``. By default, all algorithms are evaluated.
- ``--databases``: Specify a list of databases that you want evaluate. Possible values are ``BANCA`` and ``GBU``. By default, both databases are evaluated.
- ``--gbu-plot-file`` (only valid if GBU is in the databases): The file that should contain the plot for the GBU database. The default is GBU.pdf
- ``--verbose``: Print out additional information or debug information during the evaluation of the experiments. The ``--verbose`` option can be used several times, increasing the level to Warning (1), Info (2), Debug (3). By default, only Error (0) messages are printed.

The most simple way to regenerate the results is, hence:

.. code-block:: sh

  $ bin/befit2012_execute.py --result-directory [results] --temp-directory [temp] -vv

  ... take a trip to the Caribbean islands ...

  $ bin/befit2012_evaluate.py --result-directory [results] -vv


Expected Results
''''''''''''''''
The expected resulting plots of the GBU database are:

.. image:: Good.png
  :width: 33%
.. image:: Bad.png
  :width: 33%
.. image:: Ugly.png
  :width: 33%


.. table:: Results of the GBU database in terms of CAR at 0.1% FAR

  +-----------++-------+-------+-------+
  | Algorithm || Good  | Bad   | Ugly  |
  +===========++=======+=======+=======+
  |   Graphs  || 71.9% | 13.7% |  3.1% |
  +-----------++-------+-------+-------+
  |    ISV    || 80.7% | 22.8% |  4.2% |
  +-----------++-------+-------+-------+
  |  LDA-IR   || 84.6% | 49.5% | 11.7% |
  +-----------++-------+-------+-------+
  |  LGBPHS   || 66.6% | 12.3% |  2.7% |
  +-----------++-------+-------+-------+

The expected EER and HTER results of the BANCA database are:

.. table:: Results of the BANCA database (protocol *P*) in EER (development set) and HTER (evaluation set)

  +-----------++-------+-------+
  | Algorithm || EER   | HTER  |
  +===========++=======+=======+
  |   Graphs  || 11.7% | 12.4% |
  +-----------++-------+-------+
  |    ISV    ||  9.9% | 10.5% |
  +-----------++-------+-------+
  |  LDA-IR   || 26.3% | 27.0% |
  +-----------++-------+-------+
  |  LGBPHS   || 13.2% | 16.1% |
  +-----------++-------+-------+

.. note::
  These results are generated with Bob_ version 1.2.0, FaceRecLib_ version 1.1.3 and the January 2012 release of the `CSU Face Recognition Resources`_.
  These results partially do not correspond to the ones published in the Paper [GWM12]_, which were generated with older versions of Bob_ and of the `CSU Face Recognition Resources`_.
  Specifically:

  1. The random initialization of the ISV procedure changed.
     Therefore, ISV results differ slightly.

  2. I don't know exactly, what was changed in the `CSU Face Recognition Resources`_, but now our results on the GBU database correspond roughly to the ones published by the authors of the CSU toolkit in [LBP+12]_.

  Be aware that running the experiments with different versions of the source code might generate other results.
  Therefore, we have pin-pointed these versions in the ``install_requires`` section of the setup.py_ file.

.. [GWM12]   *M. Günther, R. Wallace and S. Marcel*. **An Open Source Framework for Standardized Comparisons of Face Recognition Algorithms**. Computer Vision - ECCV 2012. Workshops and Demonstrations, LNCS, 7585, 547-556, 2012.
.. [LBP+12]  *Y.M. Lui, D.S. Bolme, P.J. Phillips, J.R. Beveridge and B.A. Draper*. **Preliminary studies on the Good, the Bad, and the Ugly face recognition challenge problem**. Computer Vision and Pattern Recognition Workshops (CVPRW), pages 9-16. 2012.

.. include:: links.rst

