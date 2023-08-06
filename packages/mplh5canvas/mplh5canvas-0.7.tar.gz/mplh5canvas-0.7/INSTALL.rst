Requirements
------------

We have tried to keep this module as free of dependencies as possible in order
to open up the widest possible installation base. We do however depend
on the excellent `pywebsocket`_ code for handling our browser
communications. This allows us to better track the WebSocket standard
as it continues to evolve.

The current base system requirements prior to installation are:

* Python 2.5, 2.6 or 2.7 (2.4 should also be OK, but has not been tested)
* `matplotlib`_ 0.99.1.1 or newer (will be automatically installed if you are going the *easy_install mplh5canvas* route)
* `pywebsocket`_ 0.6 or newer (will be automatically installed if you are going the *easy_install mplh5canvas* route)

If you want to make use of *easy_install* as suggested in the instructions below, you should install `setuptools`_. Alternatively you can use *pip* instead of *easy_install* by installing the `pip`_ Python package.

The web browser you use to display the plots must support Canvas and WebSocket
(see http://caniuse.com/#feat=websockets for a summary of current WebSocket
support). The status quo for the major browsers in July 2013 is:

* **Chrome 9 and later** works out of the box and is the target browser (both desktop and mobile versions)

* **Safari 5 and later** works out of the box (both Mac OS X and iOS versions)

* **Firefox 4** works after unblocking WebSocket support:

    - Browse to the ``about:config`` preferences page and promise to be careful
    - Type ``websocket`` in the filter to find the right option
    - Double-click on ``network.websocket.override-security-block`` to set it to ``true``

* **Firefox 5 to 10** is not supported due to a custom ``MozWebSocket`` class

* **Firefox 11 and later** works out of the box

* **Opera 11 to 12.02** works after unblocking WebSocket support:

    - Browse to the Preference Editor at the ``opera:config`` page
    - Type ``websocket`` in the "Quick find" search field to zoom in on the
      right option ("Enable WebSockets" under User Prefs)
    - Check the tickbox and click on the Save button

* **Opera 12.10 and later** works out of the box

* **Internet Explorer 10 and later** should work out of the box but is untested

* **Opera Mini** and **Android Browser** have no WebSocket support yet and are therefore not supported

netifaces
^^^^^^^^^

It is surprisingly difficult to make a good guess of the IP address of a user's
primary network interface across a range of operating systems. The code uses
``socket.gethostbyname`` by default, which does a reasonable job but is
completely borked if you have VMware installed.

If available it will use the `netifaces`_ module which generally does a better
job. It is recommended that you install this by running::

  easy_install netifaces

mod_pywebsocket
^^^^^^^^^^^^^^^

This will be installed along with mplh5canvas if you follow the instructions below.
However, you can install it yourself::

    easy_install mod_pywebsocket

The `mod_pywebsocket PyPI`_ page may be out of date as we maintain this ourselves. The master
repository for mod_pywebsocket is at `pywebsocket`_.

Installation
------------

Since this package is available on `PyPI`_ the simplest way to install it is to do::

  easy_install mplh5canvas

Alternatively, install mod_pywebsocket yourself, download the latest mplh5canvas tarball (or check out the source code) from the `Google Code`_ page and do::

  python setup.py install

It is assumed that you have the proper permissions to install Python packages on
your system (if not, you can make use of `virtualenv`_ instead).

Testing
-------

We provide a number of example scripts for initial testing. Surprisingly these
are found in the ``examples`` directory of the source code.

The script names are self-explanatory. The URL of the management server should be
printed out by the script, and if a web browser is installed and available a new
tab should be opened in your browser. If not, then just copy and paste the
management URL into a browser window.

Conformance Testing
^^^^^^^^^^^^^^^^^^^

To try and reach a level of reasonable conformance we have a crude test suite
that will run against a directory of matplotlib examples and produce a web page
for side-by-side comparison::

  cd tests
  python test.py -d <matplotlib source tree>/lib/mpl_examples/pylab_examples

This produces output files in the ``tests/output`` directory. The file ``test.html``
when viewed in a web browser will show the mplh5canvas implementation alongside a
PNG and SVG for each file in the target directory. 

Be aware that these test results can be pretty massive and may well lead to
browser instability. You can run on a restricted set of tests by using a wildcard
parameter (see ``test.py --help``).

There is also the option of rendering each canvas on the page to a PNG for easier
side-by-side comparison. To do this, run::

  python rec.py

once you have a completed test run. At the bottom of the test.html page click
the "Connect" button. Then click the "Put Images to Server" button.
The ``rec.py`` instance should indicate a variety of files being written to disk.
Then open the ``test_rendered.html`` page which will have a side-by-side column
of PNGs.

.. _pywebsocket: http://code.google.com/p/pywebsocket/
.. _matplotlib: http://matplotlib.sourceforge.net/
.. _setuptools: https://pypi.python.org/pypi/setuptools
.. _pip: http://www.pip-installer.org/
.. _netifaces: http://alastairs-place.net/netifaces/
.. _mod_pywebsocket PyPI: https://pypi.python.org/pypi/mod_pywebsocket
.. _PyPI: https://pypi.python.org/pypi/mplh5canvas
.. _Google Code: https://code.google.com/p/mplh5canvas
.. _virtualenv: https://pypi.python.org/pypi/virtualenv
