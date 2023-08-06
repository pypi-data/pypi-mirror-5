.. _workflow:

Development Workflow
====================

This section documents the workflow that the LEAP project team follows and expects for the code contributions.

Code formatting
---------------
In one word: `PEP8`_.

`autopep8` might be your friend. or eat your code.

.. _`PEP8`: http://www.python.org/dev/peps/pep-0008/
.. _`autopep8`: http://pypi.python.org/pypi/autopep8

Dependencies
------------
If you introduce a new dependency, please add it under ``pkg/requirements`` or ``pkg/test-requirements`` as appropiate, under the proper module section.

Git flow
--------
We are basing our workflow on what is described in `A successful git branching model <http://nvie.com/posts/a-successful-git-branching-model/>`_.

.. image:: https://leap.se/code/attachments/13/git-branching-model.png

The author of the aforementioned post has also a handy pdf version of it: `branching_model.pdf`_ 

However, we use a setup in which each developer maintains her own feature branch in her private repo. After a code review, this feature branch is rebased onto the authoritative integration branch. Thus, the leapcode repo in leap.se (mirrored in github) only maintains the master and develop branches.

A couple of tools that help to follow this process are  `git-flow`_ and `git-sweep`_.

.. _`branching_model.pdf`: https://leap.se/code/attachments/14/Git-branching-model.pdf
.. _`git-flow`: https://github.com/nvie/gitflow
.. _`git-sweep`: http://pypi.python.org/pypi/git-sweep

Code review and merges into integration branch
-----------------------------------------------
All code ready to be merged into the integration branch is expected to:

* Have tests
* Be documented
* Pass existing tests: do **run_tests.sh** and **tox -v**. All feature branches are automagically built by our `buildbot farm <http://lemur.leap.se:8010/grid>`_. So please check your branch is green before merging it it to `develop`. Rebasing against the current tip of the integration when possible is preferred in order to keep a clean history.
