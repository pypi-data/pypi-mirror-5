Bitmask
=======
*your internet encryption toolkit*

.. image:: https://pypip.in/v/leap.bitmask/badge.png
        :target: https://crate.io/packages/leap.bitmask

**Bitmask** is the multiplatform desktop client for the services offered by
`the LEAP Platform`_.
It is written in python using `PySide`_ and licensed under the GPL3.
Currently we distribute pre-compiled bundles for Linux and OSX, with Windows
bundles following soon.

.. _`PySide`: http://qt-project.org/wiki/PySide
.. _`the LEAP Platform`: https://github.com/leapcode/leap_platform


Read the Docs!
------------------

The latest documentation is available at `Read The Docs`_.

.. _`Read The Docs`: http://bitmask.rtfd.org

Dependencies
------------------

Bitmask depends on these libraries:

* ``python 2.6`` or ``2.7``
* ``qt4 libraries``
* ``libopenssl``
* ``openvpn``

Python packages are listed in ``pkg/requirements.pip`` and ``pkg/test-requirements.pip``

Debian
^^^^^^

With a Debian based system, to be able to run Bitmask you need to run the following command::

  $ sudo apt-get install openvpn python-pyside pyside-tools python-setuptools python-all-dev python-pip python-dev python-openssl

Installing
-----------

After getting the source and installing all the dependencies, proceed to install ``bitmask`` package::

  $ make
  $ sudo LEAP_VENV_SKIP_PYSIDE=1 python setup.py install

Running
-------

After a successful installation, there should be a launcher called ``bitmask`` somewhere in your path::

  $ bitmask

If you are testing a new provider and do not have a CA certificate chain tied to your SSL certificate, you should execute Bitmask in the following way::

  $ bitmask --danger

But **DO NOT use it on a regular bases**.

**WARNING**: If you use the --danger flag you may be victim to a MITM_ attack without noticing. Use at your own risk.

.. _MITM: http://en.wikipedia.org/wiki/Man-in-the-middle_attack

Hacking
=======

The Bitmask git repository is available at::

  git://leap.se/leap_client

Some steps need to be run when setting a development environment for the first time.

Enable a **virtualenv** to isolate your libraries. (Current *.gitignore* knows about a virtualenv in the root tree. If you do not like that place, just change ``.`` for *<path.to.environment>*)::

  $ virtualenv .
  $ source bin/activate

Make sure you are in the development branch::

  (bitmask)$ git checkout develop

Symlink your global pyside libraries::

  (bitmask)$ pkg/postmkvenv.sh

And make your working tree available to your pythonpath::

  (bitmask)$ python setup.py develop

Run Bitmask::

  (bitmask)$ python src/leap/app.py -d


If you are testing a new provider that doesn't have the proper certificates yet, you can use --danger flag, but **DO NOT use it on a regular bases**.

**WARNING**: If you use the --danger flag you may be victim to a MITM_ attack without noticing. Use at your own risk.

.. _MITM: http://en.wikipedia.org/wiki/Man-in-the-middle_attack

Testing
=======

Have a look at ``pkg/test-requirements.pip`` for the tests dependencies.

To run the test suite::

    $ ./run_tests.sh

which the first time should automagically install all the needed dependencies in your virtualenv for you.

License
=======

.. image:: https://raw.github.com/leapcode/leap_client/develop/docs/user/gpl.png

Bitmask is released under the terms of the `GNU GPL version 3`_ or later.

.. _`GNU GPL version 3`: http://www.gnu.org/licenses/gpl.txt
