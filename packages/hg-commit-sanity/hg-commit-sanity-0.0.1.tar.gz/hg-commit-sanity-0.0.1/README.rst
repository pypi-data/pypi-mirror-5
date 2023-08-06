hg-commit-sanity: Mercurial Commit Sanity
=========================================

.. image:: https://api.travis-ci.org/paylogic/hg-commit-sanity.png
   :target: https://travis-ci.org/paylogic/hg-commit-sanity
.. image:: https://pypip.in/v/hg-commit-sanity/badge.png
   :target: https://crate.io/packages/hg-commit-sanity/
.. image:: https://coveralls.io/repos/paylogic/hg-commit-sanity/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/hg-commit-sanity

``hg-commit-sanity`` is a Mercurial extension that allows to easily create precommit hooks to do sanity checks on commits.

Kudos to `Matthew Schinckel <http://schinckel.net/2013/04/07/hg-commit---prevent-stupidity>`_

Installation
------------

.. sourcecode ::

    pip install hg-commit-sanity

Configuration
-------------

An example of your .hgrc:

.. code-block:: cfg

    [extensions]
    hg_commit_sanity =

    [hg_commit_sanity]
    .py =
        ^[^#]*import pdb; pdb.set_trace\(\)
    .js =
        ^[^(//)]*console\.[a-zA-Z]+\(.*\)

This will Abort the commit in case it will find import pdb; pdb.set_trace() in *.py files and console. in *.js files

Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on the `GitHub project page <http://github.com/paylogic/hg-commit-sanity>`_.

License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See LICENSE.txt

© 2013 Paylogic International.
