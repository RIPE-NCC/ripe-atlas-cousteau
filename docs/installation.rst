.. _requirements-and-installation:

Requirements & Installation
***************************

.. _installation-requirements:

Requirements
============

As you might have guessed, with all of the magic going on under the hood, there
are a few dependencies:

* `python-dateutil`_
* `socketIO-client>=0.6.5`_
* `requests>=2.7.0`_

Additionally, we recommend that you also install `sphinx`_ if you intend to build the
documentation files for offline use.

.. _python-dateutil: https://pypi.python.org/pypi/python-dateutil/
.. _socketIO-client>=0.6.5: https://pypi.python.org/pypi/socketIO-client
.. _requests>=2.7.0: https://pypi.python.org/pypi/requests
.. _sphinx: https://pypi.python.org/pypi/Sphinx/


.. _installation:

Installation
============

Installation should be easy, though it may take a while to install all of the
aforementioned requirements.  Using pip is the recommended method.


.. _installation-from-pip:

Using pip
---------

The quickest and easiest way to install Sagan is to use ``pip``::

    $ pip install ripe.atlas.cousteau


.. _installation-from-github:

From GitHub
-----------

If you're feeling a little more daring and want to use whatever is on GitHub,
you can have pip install right from there::

    $ pip install git+https://github.com/RIPE-NCC/ripe-atlas-cousteau.git


.. _installation-from-tarball:

From a Tarball
--------------

If for some reason you want to just download the source and install it manually,
you can always do that too.  Simply un-tar the file and run the following in the
same directory as ``setup.py``.::

    $ python setup.py install


