Pylibsass 
=========

.. image:: https://travis-ci.org/rsenk330/pylibsass.png?branch=master
        :target: https://travis-ci.org/rsenk330/pylibsass

.. image:: https://pypip.in/d/pylibsass/badge.png
        :target: https://crate.io/packages/pylibsass

Pylibsass is a Python wrapper around the 
`libsass <https://github.com/hcatlin/libsass>`_ library. The main goal of this
library is to provide an easy way to hook SASS compilation into your projects.

It uses the awesome `Watchdog <http://pythonhosted.org/watchdog/>`_ library to
detect filesystem changes and recompile whenever there are changes detected.

.. code-block:: python

    import pylibsass

    pylibsass.watch("app/static/scss", "app/static/css")

Installation
------------

Installation is easy:

.. code-block:: bash

    $ pip install pylibsass

Documentation
-------------

You can view the documentation on `Read the Docs <https://pylibsass.readthedocs.org/>`_.

Development
-----------

Installing from source is easy. It is recommended to do this from within a 
virtualenv:

.. code-block:: bash

    $ python setup.py develop

To run the tests, you do something similar:

.. code-block:: bash

    $ python setup.py test

Contributing
------------

#. `Fork it! <https://help.github.com/articles/fork-a-repo>`_
#. Create your feature branch (`git checkout -b my-new-feature`)
#. Commit your changes (`git commit -am 'Added some feature'`)
#. Push to the branch (`git push origin my-new-feature`)
#. Create new Pull Request
