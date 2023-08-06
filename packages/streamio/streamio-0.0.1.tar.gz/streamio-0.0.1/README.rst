.. _Python: http://www.python.org/
.. _funcy: http://pypi.python.org/pypi/funcy
.. _py: http://pypi.python.org/pypi/py
.. _Griffith University: http://www.griffith.edu.au/
.. _TerraNova: https://terranova.org.au/
.. _Climate Change and Adaptation Visualization: http://ccav.terranova.org.au/
.. _Project Website: http://bitbucket.org/prologic/streamio
.. _PyPi Page: http://pypi.python.org/pypi/streamio
.. _Read the Docs: http://streamio.readthedocs.org/en/latest/
.. _Downloads Page: https://bitbucket.org/prologic/streamio/downloads


streamio is a simple library of functions designed to read, write and sort large files using iterators so that the operations will successfully complete
on systems with limited RAM. This library has been used extensively at `Griffith University`_ whilst developing the `TerraNova`_
`Climate Change and Adaptation Visualization`_ tool(s) and processing large volumes of data. streamio is written in `Python`_ and has extensive documentation
and unit tests with 100% coverage.

streamio currently has the following functionality available:

- ``stream`` - read large files as an iterative stream.
- ``jsonstream`` - read large files as a json stream where each line in the file is valid json.
- ``csvstream`` - read large csv files as a stream interpreteing as csv.
- ``csvdictstream`` - read large csv files as a stream interpreteing as csv and yielding dicts.
- ``merge`` - take a list of ordered iterables and return a single ordered generator (*similar to heapq.merge but with key support*)
- ``mergesort`` - given a large unsorted input file, split into chunks, sort and merge sort the result into an output file.
- ``minmax`` - compute the min and max of a given iterable all at once


- Visit the `Project Website`_
- `Read the Docs`_
- Download it from the `Downloads Page`_

.. image:: https://pypip.in/v/streamio/badge.png
   :target: https://crate.io/packages/streamio/
   :alt: Latest PyPI version

.. image:: https://pypip.in/d/streamio/badge.png
   :target: https://crate.io/packages/streamio/
   :alt: Number of PyPI downloads

.. image:: https://jenkins.shiningpanda-ci.com/prologic/job/streamio/badge/icon
   :target: https://jenkins.shiningpanda-ci.com/prologic/job/streamio/
   :alt: Build Status


Requirements
------------

- `funcy`_
- `py`_

streamio also comes with documentation and a full comprehensive unit test suite which require the following:

To build the docs:

- `sphinx <https://pypi.python.org/pypi/Sphinx>`_

To run the unit tests:

- `pytest <https://pypi.python.org/pypi/pytest>`_


Installation
------------

The simplest and recommended way to install streamio is with pip.
You may install the latest stable release from PyPI with pip::

    > pip install streamio

If you do not have pip, you may use easy_install::

    > easy_install streamio

Alternatively, you may download the source package from the
`PyPI Page`_ or the `Downloads page`_ on the `Project Website`_;
extract it and install using::

    > python setup.py install

You can also install the
`latest-development version <https://bitbucket.org/prologic/streamio/get/tip.tar.gz#egg=streamio-dev>`_ by using ``pip`` or ``easy_install``::
    
    > pip install streamio==dev

or::
    
    > easy_install streamio==dev


For further information see the `streamio documentation <http://streamio.readthedocs.org/>`_.


Supported Platforms
-------------------

- Linux, FreeBSD, Mac OS X
- Python 2.7
- PyPy 2.2

**Windows**: We acknowledge that Windows exists and make reasonable efforts
             to maintain compatibility. Unfortunately we cannot guarantee
             support at this time.
