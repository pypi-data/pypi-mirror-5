django-treebeard
================

`django-treebeard <https://tabo.pe/projects/django-treebeard/>`_
is a library that implements efficient tree implementations for the
`Django Web Framework 1.4+ <http://www.djangoproject.com/>`_, written by
`Gustavo Picón <https://tabo.pe>`_ and licensed under the Apache License 2.0.

``django-treebeard`` is:

- **Flexible**: Includes 3 different tree implementations with the same API:

  1. :doc:`Adjacency List <al_tree>`
  2. :doc:`Materialized Path <mp_tree>`
  3. :doc:`Nested Sets <ns_tree>`

- **Fast**: Optimized non-naive tree operations (see :doc:`benchmarks`).
- **Easy**: Uses `Django Model Inheritance with abstract classes`_ 
  to define your own models.
- **Clean**: Testable and well tested code base. Code/branch test coverage
  is above 96%. Tests are available in Jenkins:

  - `Tests running on different versions of Python, Django and DB engines`_
  - `Code Quality`_


Contents
--------

.. toctree::
   :maxdepth: 2

   intro
   api
   mp_tree
   ns_tree
   al_tree
   admin
   forms
   exceptions
   caveats
   benchmarks
   tests
   changes


.. _`Django Model Inheritance with abstract classes`:
   https://docs.djangoproject.com/en/1.4/topics/db/models/#abstract-base-classes
.. _`Tests running on different versions of Python, Django and DB engines`:
   https://tabo.pe/jenkins/job/django-treebeard/
.. _`Code Quality`: https://tabo.pe/jenkins/job/django-treebeard-quality/


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
