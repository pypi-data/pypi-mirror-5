=============================================================================
 Counter-Measures to 3D Facial Mask Attacks using Local Binary Patterns (LBP)
=============================================================================

This package implements the LBP counter-measure to spoofing attacks with 3d masks to 2d face recognition systems as described in the paper `Spoofing in 2D Face Recognition with 3D Masks and Anti-spoofing with Kinect`, by N. Erdogmus and S. Marcel, presented at BTAS 2013.

If you use this package and/or its results, please cite the following publications:

1. The original paper with the counter-measure explained in details::

    @INPROCEEDINGS{Erdogmus_BTAS_2013,
    author = {Erdogmus, Nesli and Marcel, S{\'{e}}bastien},
    keywords = {3D Mask Attack, Counter-Measures, Counter-Spoofing, Face Recognition, Liveness Detection, Replay, Spoofing},
    month = sep,
    title = {Spoofing in 2D Face Recognition with 3D Masks and Anti-spoofing with Kinect},
    journal = {BTAS 2013},
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

If you wish to report problems or improvements concerning this code, please contact the authors of the above mentioned papers.

Raw data
--------

The data used in the paper is publicly available and should be downloaded and installed **prior** to try using the programs described in this package. Visit `the 3D MASK ATTACK database portal <https://www.idiap.ch/dataset/3dmad>`_ for more information.

Installation
------------

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI, note **the development tip of the package may not be stable** or become unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/maskattack.lbp  <http://pypi.python.org/pypi/maskattack.lbp>`_ to download the latest stable version of this package.

There are 2 options you can follow to get this package installed and operational on your computer: you can use automatic installers like `pip <http://pypi.python.org/pypi/pip/>`_ (or `easy_install <http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a virtual work environment just for this package.

Using an automatic installer
============================

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install maskattack.lbp

You can also do the same with ``easy_install``::

  $ easy_install maskattack.lbp

This will download and install this package plus any other required dependencies. It will also verify if the version of Bob you have installed is compatible.

This scheme works well with virtual environments by `virtualenv <http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
=====================

Download the latest version of this package from `PyPI <http://pypi.python.org/pypi/maskattack.lbp>`_ and unpack it in your working area. The installation of the toolkit itself uses `buildout <http://www.buildout.org/>`_. You don't need to understand its inner workings to use this package. Here is a recipe to get you started::
  
  $ python bootstrap.py 
  $ ./bin/buildout

These 2 commands should download and install all non-installed dependencies and get you a fully operational test and development environment.

.. note::

  The python shell used in the first line of the previous command set determines the python interpreter that will be used for all scripts developed inside this package. Because this package makes use of `Bob <http://idiap.github.com/bob>`_, you must make sure that the ``bootstrap.py`` script is called with the **same** interpreter used to build Bob, or unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to consider it uses the default python interpreter. In this case, the above 3 command lines should work as expected. If you have Bob installed somewhere else on a private directory, edit the file ``buildout.cfg`` **before** running ``./bin/buildout``. Find the section named ``external`` and edit the line ``egg-directories`` to point to the ``lib`` directory of the Bob installation you want to use. For example::

    [external]
    recipe = xbob.buildout:external
    egg-directories=/Users/crazyfox/work/bob/build/lib

User Guide
----------

This section explains how to use the package in order to: a) calculate the LBP features on the 3D Mask Attack database; b) perform classification using Chi-2, Linear Discriminant Analysis (LDA) and Support Vector Machines (SVM).

It is assumed you have followed the installation instructions for the package, and got the required database downloaded and uncompressed in a directory. After running the ``buildout`` command, you should have all required utilities sitting inside the ``bin`` directory. We expect that the video files of the database are installed in a sub-directory called ``database`` at the root of the package. You can use a link to the location of the database files, if you don't want to have the database installed on the root of this package::

  $ ln -s /path/where/you/installed/the/database database

If you don't want to create a link, use the ``--input-dir`` flag (available in all the scripts) to specify the root directory containing the database files.

Calculate the LBP features
==========================

The first stage of the process is calculating the feature vectors, which are essentially normalized LBP histograms. A single feature vector for each frame of the video (both for the depth and color images) is computed and saved as a multiple row array in a single file. 

The program to be used for this is ``./bin/calclbp.py``. It uses the utility script ``spoof/calclbp.py``. Depending on the command line arguments, it can compute different types of LBP histograms over the normalized face bounding box. Cropped and normalized images can be saved to a folder (``./img_cropped`` by default) and used in future computations to skip cropping using ``-sc`` flag.

Furthermore, the normalized face-bounding box can be divided into blocks or not.

The following commands will calculate the feature vectors of all the videos in the database and will put the resulting ``.hdf5`` files with the extracted feature vectors in the output directory ``./lbp_features/r_1`` with and without skipping the cropping step::

  $ bin/calclbp.py -ld ./lbp_features/r_1 --el regular
  
  $ bin/calclbp.py -cd ./img_cropped -ld ./lbp_features/r_1 --el regular -sc

In the above command, the program will crop (64x64 by default) and normalize the images according to the eye positions available in the database. The cropped images will be saved to the default directory (``img_cropped``) which can be changed using ``--cropped-dir`` argument.

To see all the options for the script ``calclbp.py``, just type ``--help`` at the command line. Change the default option in order to obtain various features described  in the paper.

Classification using Chi-2 distance
===================================

The clasification using Chi-2 distance consists of two steps. The first one is creating the histogram model (average LBP histogram of all the real access videos in the training set). The second step is comparison of the features of development and test videos to the model histogram and writing the results.

The script for performing Chi-2 histogram comparison is ``./bin/cmphistmodels.py``. It expects that the LBP features of the videos are stored in a folder ``./bin/lbp_features``. 

First, it calculates the average real-access histogram using the training set and next, it computes the distances and writes the results in a file using the utility script ``spoof/chi2.py`. The default input directory is ``./lbp_features``, while the default output directory is ``./res``. To execute this script on previously extracted features, just run:: 

  $ ./bin/cmphistmodels.py -v ./lbp_features/r_1

To see all the options for the script ``cmphistmodels.py``, just type ``--help`` at the command line.

Classification with linear discriminant analysis (LDA)
======================================================

The classification with LDA is performed using the script ``./bin/ldatrain_lbp.py``. It makes use of the scripts ``ml/lda.py``, ``ml/pca.py`` (if PCA reduction is performed on the data) and ``ml/norm.py`` (if the data need to be normalized). The default input and output directories are ``./lbp_features`` and ``./res``. To execute the script with prior PCA dimensionality reduction as is done in the paper, call::

  $ ./bin/ldatrain_lbp.py -v ./lbp_features/r_1 -r

To see all the options for this script, just type ``--help`` at the command line.

Classification with support vector machine (SVM)
================================================

The classification with SVM is performed using the script ``./bin/svmtrain_lbp.py``. It makes use of the scripts ``ml/pca.py`` (if PCA reduction is performed on the data) and ``ml\norm.py`` (if the data need to be normalized). The default input and output directories are ``./lbp_features`` and ``./res``. To execute the script as is done in the paper, call::

  $ ./bin/svmtrain_lbp.py -v ./lbp_features/r_1

To see all the options for this script, just type ``--help`` at the command line.

Plotting the HTER
=================
The classification scripts ``cmphistmodels``, ``ldatrain_lbp`` and ``svmtrain_lbp``, run the experiments in 1000-fold manner, by randomly assigning subject ids to training, development and test sets (of fixed size). The resulting files are written to the ``res`` folder by default. If all the experiments in the paper are run (3 classification, 4 LBP methods with and without blocks - see ``run_experiments.sh``), the ``barplot.py`` script will create and save the image with HTER bar plot (under the ``res`` folder), for which the height shows the mean of the HTER values in 1000 folds and the error bar shows the standard deviation::

  $ ./bin/barplot.py


Problems
--------

In case of problems, please contact any of the authors of the paper.
