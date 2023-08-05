Charlatan: Fixtures Made Easy
=============================

**Efficiently manage and install data fixtures**

`Charlatan` is a library that you can use in your tests to create database
fixtures. Its aim is to provide a pragmatic interface that focuses on making it
simple to define and install fixtures for your tests. It is also agnostic in so
far as even though it's designed to work out of the box with SQLAlchemy models,
it can work with pretty much anything else.

Documentation
-------------

Latest documentation: `uber.github.io/charlatan <http://uber.github.io/charlatan/>`_

Getting started
---------------

.. code-block:: python

    import unittest

    from toaster.models import db_session

    import charlatan

    charlatan.load("./tests/data/fixtures.yaml",
                   models_package="toaster.models",
                   db_session=db_session)


    class TestToaster(unittest.TestCase, charlatan.FixturesManagerMixin):

        def setUp(self):
            self.clean_fixtures_cache()
            self.install_fixtures(("toaster", "user"))

        def test_toaster(self):
            """Verify that toaster can toast."""

            self.toaster.toast()

Installation
------------

For now, you need to install `charlatan` by adding the following to your
``requirements.txt``::

    -e git+git@github.com:uber/charlatan.git#egg=charlatan

License
-------

charlatan is available under the MIT License.

Copyright Uber 2013, Charles-Axel Dein <charles@uber.com>

Authors
-------

Charles-Axel Dein <charles@uber.com>
