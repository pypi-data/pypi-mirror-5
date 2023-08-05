Installation
============

Installation
------------

Install Motor from PyPI_ with pip_::

  $ pip install motor

Pip automatically installs Motor's prerequisite packages, `PyMongo 2.5.0`_,
Greenlet_, and Tornado_.

Prerequisites
-------------

* CPython 2.5, 2.6, 2.7, or 3.3
* Although Motor works with PyPy 2.0-beta1, limitations with greenlets and
  PyPy's JIT compiler make PyPy applications that use Motor too slow for
  regular use
* `PyMongo 2.5.0`_ exactly
* Tornado_
* Greenlet_

Tests require Nose_ and generating the docs_ requires Sphinx_.

.. _PyPI: http://pypi.python.org/pypi/motor

.. _pip: http://pip-installer.org

.. _PyMongo 2.5.0: https://pypi.python.org/pypi/pymongo/2.5

.. _Tornado: http://www.tornadoweb.org

.. _Greenlet: http://pypi.python.org/pypi/greenlet/

.. _Nose: http://pypi.python.org/pypi/nose/

.. _docs: http://motor.readthedocs.org

.. _Sphinx: http://sphinx-doc.org/
