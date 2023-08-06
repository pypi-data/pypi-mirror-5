textteaser is a package for summarizing text using the TextTeaser API.

See:

* https://www.mashape.com/mojojolo/textteaser

for more information and to get an API key.

Documentation is available on Read the Docs:

* https://py-textteaser.readthedocs.org/

.. include:: INSTALL.rst

.. include:: CHANGELOG.rst

Development
===========

All development for textteaser takes place on bitbucket:

* https://bitbucket.org/jgoettsch/py-textteaser/

To get started you can do the following::

    $ hg clone https://bitbucket.org/jgoettsch/py-textteaser/
    $ cd py-textteaser
    $ pip install -r requirements_dev.txt
    $ python setup.py develop

If you discover a bug, please create an issue ticket:

* https://bitbucket.org/jgoettsch/py-textteaser/issues/new

To run the test suite, you will have to create a module at::

    textteaser/tests/apikey.py

with a global variable, APIKEY, which is a string containing your API key.
Then you can run the test suite with nosetests::

    $ nosetests --with-coverage --cover-package=textteaser textteaser/tests/tests.py

or through setup.py::

    $ python setup.py test
