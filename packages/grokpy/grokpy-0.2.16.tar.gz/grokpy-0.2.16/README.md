grok-py
=======

The Python client library for the
[Grok REST API](https://www.groksolutions.com/docs/devs/api/).  See
https://www.groksolutions.com/devs/ for additional resources.

[![Build Status](https://travis-ci.org/numenta/grok-py.png?branch=master)](https://travis-ci.org/numenta/grok-py)

Installation
------------

grokpy includes a
[setuptools](https://pypi.python.org/pypi/setuptools)-compatible setup.py for
your convenience.  Dependencies are listed in setup.py and will be installed
automatically as part of any of the techniques listed below.  Otherwise, you
will need to install the following external dependencies before using grokpy:

* [requests](https://pypi.python.org/pypi/requests)
* [certifi](https://pypi.python.org/pypi/certifi)
* [nose](https://pypi.python.org/pypi/nose)

*Note: These instructions assume admin-level rights (sudo).  Each of the
options listed below support alternative installation locations that do not
require admin rights.*

### From source (includes sample app):

Clone the repository or download and extract the grokpy package from
[github](https://github.com/numenta/grok-py), and run:

    sudo python setup.py install

### Development mode:

Clone the repository and run:

    sudo python setup.py develop

In development mode, you are free to make changes and have those changes apply
instantly and universally without having to repeat another build and install
phase.  This is the preferred installation approach if you are actively making
changes to the grok-py source code.

You may also want to consider using
[virtualenv](https://pypi.python.org/pypi/virtualenv) during the course of
development to create an isolated environment and avoid conflicting with
potentially other installed versions.  Once you have validated you changes in
your virtualenv, you can install using whichever technique suits your needs.

### easy_install from [PyPi](https://pypi.python.org/pypi/grokpy):

    sudo easy_install grokpy

### pip install from [PyPi](https://pypi.python.org/pypi/grokpy):

    sudo pip install grokpy

Running tests
-------------

An extensive unit test suite is provided.

### Using setup.py

    python setup.py test

### Using nose (with test discovery)

    nosetests

Sample App
----------

In addition to unit tests, a sample application is provided to demonstrate
basic functionality of grok-py as well as serve as a primer to the Grok API.

Add your API key to the app

 * Open HelloGrok.py in your favorite editor
 * Insert your API_KEY where it says "YOUR_API_KEY"

OR add your API key to your environment

From the command line:

    $ echo "export GROK_API_KEY=YOUR_API_KEY" >> ~/.bashrc
    $ source ~/.bashrc

Launch the app and monitor progress:

    $ python HelloGrok.py

Documentation
-------------

Complete documentation for the latest release can always be found at
http://numenta.github.io/grok-py/ or built directly from source by
running `python setup.py build_sphinx`.  For example:

    $ python setup.py build_sphinx
    running build_sphinx
    creating build/sphinx
    creating build/sphinx/doctrees
    creating build/sphinx/html
    Running Sphinx v1.1.3
    loading pickled environment... not yet created
    building [html]: targets for 2 source files that are out of date
    updating environment: 2 added, 0 changed, 0 removed
    reading sources... [100%] index
    looking for now-outdated files... none found
    pickling environment... done
    checking consistency... done
    preparing documents... done
    writing output... [100%] index
    writing additional files... genindex py-modindex search
    copying static files... done
    dumping search index... done
    dumping object inventory... done
    build succeeded.

Resulting HTML output can be found in `build/sphinx/html/`