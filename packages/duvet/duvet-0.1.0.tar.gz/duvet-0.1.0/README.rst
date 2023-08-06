Duvet
=====

Duvet is a GUI tool for visualizing code coverage results produced by
`coverage.py`_.

Why the name Duvet? Because a duvet doesn't just provide coverage - it keeps you
warm and cozy.

.. _coverage.py: http://nedbatchelder.com/code/coverage/

Quickstart
----------

In your virtualenv, install Duvet, generate some coverage data, and then run ``duvet``::

    $ pip install duvet
    $ coverage run myscript.py arg1 arg2
    $ duvet

This will pop up a GUI window, displaying all source code in your current working
directory. Any source file mentioned in the coverage data will be highlighted in the
source file tree, with a color indicating how good the coverage is (red for bad
coverage, green for perfect coverage). If you select a filename in the tree, the
contents of that file will be displayed, with the missed lines highlighted.

Problems under Ubuntu/Debian
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deian and Ubuntu's packaging of Python omits the ``idlelib`` library from it's
base packge. If you're using Python 2.7 on Ubuntu 13.04, you can install
``idlelib`` by running::

    $ sudo apt-get install idle-python2.7

For other versions of Python, Ubuntu and Debian, you'll need to adjust this as
appropriate.

Problems under Windows
~~~~~~~~~~~~~~~~~~~~~~

If you're running Duvet in a virtualenv, you'll need to set an
environment variable so that Duvet can find the TCL graphics library::

    $ set TCL_LIBRARY=c:\Python27\tcl\tcl8.5

You'll need to adjust the exact path to reflect your local Python install.
You may find it helpful to put this line in the ``activate.bat`` script
for your virtual environment so that it is automatically set whenever the
virtualenv is activated.

Documentation
-------------

Documentation for Duvet can be found on `Read The Docs`_.

Community
---------

Duvet is part of the `BeeWare suite`_. You can talk to the community through:

 * `@pybeeware on Twitter`_

 * The `BeeWare Users Mailing list`_, for questions about how to use the BeeWare suite.

 * The `BeeWare Developers Mailing list`_, for discussing the development of new features in the BeeWare suite, and ideas for new tools for the suite.

Contributing
------------

If you experience problems with Duvet, `log them on GitHub`_. If you
want to contribute code, please `fork the code`_ and `submit a pull request`_.

.. _BeeWare suite: http://pybee.org
.. _Read The Docs: http://duvet.readthedocs.org
.. _@pybeeware on Twitter: https://twitter.com/pybeeware
.. _BeeWare Users Mailing list: https://groups.google.com/forum/#!forum/beeware-users
.. _BeeWare Developers Mailing list: https://groups.google.com/forum/#!forum/beeware-developers
.. _log them on Github: https://github.com/pybee/duvet/issues
.. _fork the code: https://github.com/pybee/duvet
.. _submit a pull request: https://github.com/pybee/duvet/pulls
