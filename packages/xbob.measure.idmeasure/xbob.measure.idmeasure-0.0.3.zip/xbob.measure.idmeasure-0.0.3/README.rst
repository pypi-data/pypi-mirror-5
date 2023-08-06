===================================================
Detection and Identification Rate for Bob
===================================================

This example demonstrates how to extend Bob by providing a new performance measurement 
for measuring the open-set identification

Installation
============

First, you have to install `bob <http://www.idiap.ch/software/bob>`_ following the instructions
`there <http://www.idiap.ch/software/bob/docs/releases/last/sphinx/html/Installation.html>`_.

.. note:: 

  If you are reading this page through our GitHub portal and not through PyPI,
  note **the development tip of the package may not be stable** or become
  unstable in a matter of moments.

  Go to `http://pypi.python.org/pypi/xbob.measure.idmeasure
  <http://pypi.python.org/pypi/xbob.>`_ to download the latest
  stable version of this package.

There are two options you can follow to get this package installed and 
operational on your computer: you can use automatic installers like `pip
<http://pypi.python.org/pypi/pip/>`_ (or `easy_install
<http://pypi.python.org/pypi/setuptools>`_) or manually download, unpack and 
use `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_ to create a
virtual work environment just for this package. In both cases, the two 
dependences listed above will be automatically downloaded and installed.

Using an automatic installer
----------------------------

Using ``pip`` is the easiest (shell commands are marked with a ``$`` signal)::

  $ pip install xbob.measure.idmeasure

You can also do the same with ``easy_install``::

  $ easy_install xbob.measure.idmeasure

This will download and install this package plus any other required
dependencies. It will also verify if the version of Bob you have installed
is compatible.

This scheme works well with virtual environments by `virtualenv
<http://pypi.python.org/pypi/virtualenv>`_ or if you have root access to your
machine. Otherwise, we recommend you use the next option.

Using ``zc.buildout``
---------------------

Download the latest version of this package from `PyPI
<http://pypi.python.org/pypi/xbob.measure.idmeasure>`_ and unpack it in your
working area. The installation of the toolkit itself uses `buildout
<http://www.buildout.org/>`_. You don't need to understand its inner workings
to use this package. Here is a recipe to get you started::
  
  $ python bootstrap.py 
  $ ./bin/buildout

These two commands should download and install all non-installed dependencies and 
get you a fully operational test and development environment.

.. note::

  The python shell used in the first line of the previous command set
  determines the python interpreter that will be used for all scripts developed
  inside this package. Because this package makes use of `Bob`_, you must make sure
  that the ``bootstrap.py`` script is called with the **same** interpreter used to 
  build Bob, or unexpected problems might occur.

  If Bob is installed by the administrator of your system, it is safe to
  consider it uses the default python interpreter. In this case, the above 3
  command lines should work as expected. If you have Bob installed somewhere
  else on a private directory, edit the file ``buildout.cfg`` **before**
  running ``./bin/buildout``. Find the section named ``buildout`` and edit or
  add the line ``prefixes`` to point to the directory where Bob is installed or
  built. For example::

    [buildout]
    ...
    prefixes=/Users/crazyfox/work/bob/build


User Guide
==========

It is assumed you have followed the installation instructions for the package
and got this package installed.

Two functions, DIR and DIR_plot, are in this package to compute and plot the 
detection and identification rates by given the predefined false acceptance 
rates.  The descriptions of these function are presented below.

def DIR(cmc_scores, far_list):
    Calculates the Detection and Identification Rate from the give input and 
    a vector of specified false acceptance rates
    
    Keyword attributes:

    cmc_scores
      List of two-element tuples. Each of the tuples contains the negative and 
      the positive scores for one test item.

    far_list
      Array of predefined false acceptance rates.

    Return: List of two-element tuples, namely detection and identificatio rate. 
      Each of the tuples contains the probability that the rank r of the 
      positive score and the corresponding false acceptance rate. r is computed
      as the number of negative scores that are higher than the positive score.

def DIR_plot(cmc_scores, far_list, logx = True, **kwargs):
    Plot the Detection and Identification Rate from the give input and a 
    vector of specified false acceptance rates
    
    Keyword attributes:

    cmc_scores
      List of two-element tuples. Each of the tuples contains the negative 
      and the positive scores for one test item.

    far_list
      Array of predefined false acceptance rates.

    logx
      Boolean input, if it is true, the x-axis is in log scale.

    kwargs
      A dictionary of extra plotting parameters, that is passed directly to 
      matplotlib.pyplot.plot

    Note: This function does not initiate and save the figure instance, it
          only issues the plotting commands.  Every user is responsible for
          setting up and saving the figure as it best fits his purpose.

Below, we provide an example of how to appy DIR_plot to plot the DIR curve, from 
the python universe::

  >>> import idmeasure
  # predefine a list of false acceptance rates
  >>> FAR=[.01, 0.1, 1]
  #Read The four column file needs to be in the same format as described in the
   five_column function, and the "test label" (column 4) has to contain the 
   test/probe file name.  please refer the functions of 
   bob.measure.load.cmc_four_column, bob.measure.load.cmc_five_column to load 
   or generate the "cmc scores".
  >>> idmeasure.DIR_plot(cmc_scores, FAR)
  >>>pyplot.xlabel("Rank")
  >>>pyplot.ylabel("Identification Rate (%)")
  >>>pyplot.title("Detection and Identification Rate Identification Experiment")
  >>>pyplot.grid()
  >>>pyplot.savefig("eigenfaceDIR.png")
  >>>pyplot.close()

