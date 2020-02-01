====================
pylint-forbid-import
====================

.. image:: https://dev.azure.com/selimbelhaouane/pylint-forbid-import/_apis/build/status/selimb.pylint-forbid-import?branchName=master
    :target: https://dev.azure.com/selimbelhaouane/pylint-forbid-import/_build/latest?definitionId=1&branchName=master
    :alt: Build Status

.. image:: https://img.shields.io/pypi/v/pylint_forbid_import   
    :target: https://pypi.python.org/pypi/pylint_forbid_import
    :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/pylint-forbid-import   
    :target: https://pypi.python.org/pypi/pylint_forbid_import
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/l/pylint_forbid_import
    :target: https://github.com/selimb/pylint_forbid_import/blob/master/LICENSE
    :alt: PyPI - License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: black

.. image:: assets/you_shall_not_import.jpg

A `pylint <pylint.org>`__ plugin to forbid the use of specific imports.

Useful to maintain strict(ish) separation between modules/packages of a large system.

Installation
============

Configuration
=============

Example
=======

Contributing
============

Motivation
==========

Inspired by `Monica Lent's talk <https://youtu.be/TqfbAXCCVwE?t=1553>`__, specifically on enforcing boundaries between parts of a large system using `dependency-cruiser <https://www.npmjs.com/package/dependency-cruiser>`__.

TODO