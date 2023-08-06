************
Installation
************

The recommended way to install Python packages is using a virtual environment. It has the advantage of allowing installs without the need of having root privileges, it doesn't mess up other packages in your systems and if something goes wrong it is easy to start again clean by only deleting one folder.

- Download pypi.python.org/pypi/virtualenv
- Run: virtualenv environment-name
- Run environment-name/bin/activate to activate

A thing to note is that packages installed in a virtualenv will only be available inside that virtualenv.

Once the virtual environment is set up, you can proceed with pip. It is installed by default inside virtualenvs. Otherwise, it can be downloaded from pypi.python.org/pypi/pip. Then just run in a terminal:

  ``pip install pandas``

Python version support
~~~~~~~~~~~~~~~~~~~~~~

The Toolkit has been tested on python 2.7. It *might* work on other versions.


Dependencies
~~~~~~~~~~~~

  * `pandas <http://pandas.pydata.org>`__: 0.12 or higher
  * pytest
     * Optional for tests
