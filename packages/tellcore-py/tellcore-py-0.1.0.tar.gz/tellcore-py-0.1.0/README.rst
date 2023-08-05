Python wrapper for Telldus Core
===============================

tellcore-py is a Python wrapper for `Telldus' <http://www.telldus.com/>`_ home
automation library `Telldus Core <http://developer.telldus.se/doxygen/>`_.

The module consists of a number of separate classes to make the library easier
and more python-ish to work with. See the `internals`_ section below for more
details.

* Official home page: https://github.com/erijo/tellcore-py
* Python package index: https://pypi.python.org/pypi/tellcore-py

Features
--------

* Wraps the C-interface with a python interface (with classes and exceptions).
* Automatically frees memory for returned strings.
* Throws an exception (TelldusError) in case a library function returns an
  error.
* Supports python 3 with automatic handling of strings (i.e. converting between
  bytes used by the C-library and strings as used by python).
* Takes care of making callbacks from the library thread-safe.
* Unit tested.

Users
-----

* `Tellprox <https://github.com/p3tecracknell/tellprox/>`_ - A local server to
  use in place of Tellstick Live

Example
-------

A simple example for adding a new "lamp" device, turning it on and then turning
all devices off. ::

    from tellcore.telldus import TelldusCore

    core = TelldusCore()
    lamp = core.add_device("lamp", "arctech", "selflearning-switch", house=12345, unit=1)
    lamp.turn_on()

    for device in core.devices():
        device.turn_off()

Internals
---------

At the bottom there is the Library class which is a `ctypes
<http://docs.python.org/library/ctypes.html>`_ wrapper and closely matches the
API of the underlying Telldus Core library. The library class takes care of
freeing memory returned from the base library and converts errors returned to
TelldusException. The library class is not intended to be used directly.

Instead, the TelldusCore class provides a more python-ish API on top of the
library class. This class is used for e.g. adding new devices, or enumerating
the existing devices, sensors and/or controllers. E.g. calling the devices()
method returns a list of Device instances. The Device class in turn has methods
for turning the device on, off, etc.

TODO
----

* Improve documentation.
* Add high level support for device groups.
* Refactor callback manager to ease integration with different event loops.
