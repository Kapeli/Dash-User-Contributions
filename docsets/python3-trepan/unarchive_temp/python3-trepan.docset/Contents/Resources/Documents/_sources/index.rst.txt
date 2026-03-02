.. trepan documentation master file, created by
   sphinx-quickstart on Mon Jun  1 21:23:13 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

trepan3k - a gdb-like debugger for Python 3
===========================================

trepan3k is a gdb-like debugger for Python. It is a rewrite of *pdb*
from the ground up. It is aimed for people who care about high-quality
debuggers

A command-line interface (CLI) is provided as well as an remote access
interface over TCP/IP.

See the Tutorial_ for ways to enter the debugger. See ipython-trepan_ for using this
in *ipython* or an *ipython notebook*.

This package is for Python 3. See trepan2_ for the same
code modified to work with Python 2.

An Emacs interface is available via realgud_.

.. toctree::
   :maxdepth: 2

   features
   install
   options
   entry-exit
   syntax
   commands

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _Tutorial:  https://python3-trepan.readthedocs.io/en/latest/entry-exit.html
.. _ipython-trepan: https://github.com/rocky/ipython-trepan
.. _trepan2: https://pypi.python.org/pypi/trepan2
.. _pydbgr: https://pypi.python.org/pypi/pydbgr
.. _realgud: https://elpa.gnu.org/packages/realgud.html
