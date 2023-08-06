===============================================================================
Antispoofing cross database testing
===============================================================================

This package contains scripts that permit to make a cross database testing in face antispoofing countermeasures in order evaluate them generalization power.

If you use this package and/or its results, please cite the following publications:

1. The original paper with the fusion of countermesures explained in details::

    @inproceedings{FreitasPereira_ICB_2013,
      author = {de Freitas Pereira, Tiago and Anjos, Andr{\'{e}} and De Martino, Jos{\'{e}} Mario and Marcel, S{\'{e}}bastien},
      month = Jun,
      title = {Can face anti-spoofing countermeasures work in a real world scenario?},
      journal = {International Conference on Biometrics 2013},
      year = {2013},
    }


2. Bob as the core framework used to run the experiments::

    @inproceedings{Anjos_ACMMM_2012,
      author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
      title = {Bob: a free signal processing and machine learning toolbox for researchers},
      year = {2012},
      month = oct,
      booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
      publisher = {ACM Press},
    }



Installation
------------

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/antispoofing.crossdatabase
  <http://pypi.python.org/pypi/antispoofing.crossdatabase>`_ to download the latest
  stable version of this package.

There are 2 options you can follow to get this package installed and
operational on your computer: you can use automatic installers like `pip
<http://pypi.python.org/pypi/pip/>`_ (or `easy_install
<http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and
use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a
virtual work environment just for this package.

Using an automatic installer
============================

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install antispoofing.crossdatabase

You can also do the same with ``easy_install``::

  $ easy_install antispoofing.crossdatabase

This will download and install this package plus any other required
dependencies. It will also verify if the version of Bob you have installed
is compatible.

This scheme works well with virtual environments by `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your
machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
=====================

Download the latest version of this package from `PyPI
<http://pypi.python.org/pypi/antispoofing.crossdatabase>`_ and unpack it in your
working area. The installation of the toolkit itself uses `buildout
<http://www.buildout.org/>`_. You don't need to understand its inner workings
to use this package. Here is a recipe to get you started::
  
  $ python bootstrap.py 
  $ ./bin/buildout

These 2 commands should download and install all non-installed dependencies and
get you a fully operational test and development environment.

.. note::
  The python shell used in the first line of the previous command set
  determines the python interpreter that will be used for all scripts developed
  inside this package. Because this package makes use of `Bob
  <http://idiap.github.com/bob>`_, you must make sure that the ``bootstrap.py``
  script is called with the **same** interpreter used to build Bob, or
  unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to
  consider it uses the default python interpreter. In this case, the above 3
  command lines should work as expected. If you have Bob installed somewhere
  else on a private directory, edit the file ``buildout.cfg`` **before**
  running ``./bin/buildout``. Find the section named ``buildout`` and edit or add the
  line ``prefixes`` to point to the directory where Bob is installed or built. For example::

    [buildout]
    ...
    prefixes=/Users/crazyfox/work/bob/build/lib


User Guide
----------

First of all, it is necessary to be familiarized with the satellite packages: `antispoofing.motion <http://pypi.python.org/pypi/antispoofing.motion>`_ and `antispoofing.lbptop <http://pypi.python.org/pypi/antispoofing.lbptop>`_.
The antispoofing.lbptop satellite package generates the scores of the LBP-TOP and LBP countermeasures.


Crossdatabase test
==================

The examples bellow show how to reproduce the performance using the inter-database protocol.

For each countermeasure trained and tuned with the Replay Attack Database, to get the performance using the test set of the Casia FASD, just type::

  $ ./bin/crossdb_result_analysis.py --scores-dir <scores_replay_countermeasure_directory> -d replay -t casias_fasd:

For each countermeasure trained and tuned with the Casia FASD, to get the performance using the test set of the Replay Attack Database, just type::

  $ ./bin/crossdb_result_analysis.py --scores-dir <scores_casia_countermeasure_directory> -d casia_fasd -t replay


Training all data
=================

To get the performance using a countermeasure trained and tuned with both databases (Replay Attack Database and Casia FASD) just type:

To report the results using the Replay Attack Database::

  $ ./bin/crossdb_result_analysis.py --scores-dir <scores_all_countermeasures_directory> -d all -t replay

To report the results using the Casia FASD::

  $ ./bin/crossdb_result_analysis.py --scores-dir <scores_all_countermeasures_directory> -d all -t casia_fasd


Framework
=========

For each countermeasures, to get the performance using the Score Level Fusion based Framework just type:

To report the results using the Replay Attack Database::

  $ ./bin/crossdb_fusion_framework.py --scores-dir <scores_trained_with_replay> <scores_trained_with_casia> -d all -t replay --normalizer MinMaxNorm --fusion-algorithm SUM

To report the results using the Casia FASD::

  $ ./bin/crossdb_fusion_framework.py --scores-dir <scores_trained_with_casia> <scores_trained_with_replay> -d all -t casia_fasd --normalizer MinMaxNorm --fusion-algorithm SUM


Problems
--------

In case of problems, please contact any of the authors of the paper.


