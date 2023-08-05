=======================
:mod:`z3c.recipe.mkdir`
=======================

Introduction
============

This recipe can be used to generate directories.

A short example of using the recipe within a :mod:`zc.buildout` config file:

.. code-block:: ini

   [buildout]
   parts = var

   [var]
   recipe = z3c.recipe.mkdir

This will create a directory named ``var/`` in the buildout ``parts/``
directory. If you want a different path, you can set the ``paths``
option:

.. code-block:: ini

   [buildout]
   parts = foo

   [foo]
   recipe = z3c.recipe.mkdir
   paths = foo/bar

which will create ``foo/bar/`` in the buildout root directory (not the
``parts/`` directory). Also intermediate directories are created (if
they do not exist) except you set ``create-intermediate`` option
(``yes`` by default) to ``no``.

Starting with version 0.4 you can also set the directory's user, group, and
mode, if your system supports that:

.. code-block:: ini

   [buildout]
   parts = foo

   [foo]
   recipe = z3c.recipe.mkdir
   paths = foo/bar
   user = someuser
   group = somegroup
   mode = 0750

will create any non-existing directory ``foo/`` and ``foo/bar/`` with
permissions set as told.

.. include:: ../z3c/recipe/mkdir/README.rst
