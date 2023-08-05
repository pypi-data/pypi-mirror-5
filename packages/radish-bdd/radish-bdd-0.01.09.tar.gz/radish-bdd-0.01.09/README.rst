radish
======

    ``radish`` is a "Behavior-Driven Developement"-Tool written in
    python Version: 0.01.09


--------------

**Author:** Timo Furrer tuxtimo@gmail.com **License:** GPL
**Version:** 0.01.09

What is ``radish`` ?
--------------------

``radish`` is a "Behavior-Driven Developement"-Tool written in
python. It is inspired by other ``BDD``-Tools like ``cucumber`` or
``lettuce``.

Installation
------------

There are several ways to install ``radish`` on your computer:

Simple installation with pip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is probably the simplest way to install ``radish``. Since the
``radish`` releases are hostet as well on
`pip <https://pypi.python.org/pypi/pip>`_ you can use the following
command to install ``radish``:

::

    pip install radish

*Note: On some systems you have to be root to install a package over pip.*

Manual installation from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you always want to be up to date with the newest commits you may
want to install ``radish`` directly from
`source code <https://github.com/timofurrer/radish>`_. Use the
following command sequence to clone the repository from github and
install ``radish`` afterwards:

``bash git clone https://github.com/timofurrer/radish.git ~/radish cd ~/radish git submodule init git submodule update python setup.py install``

*Note: On some systems you have to be root to install a package over setuptools.*

Update source installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have once installation ``radish`` from source you might want
to update it from time to time. Change into the directory where you
have cloned ``radish`` into (default: ``~/radish``) and pull the
newest commit from github. When you've done this you need to
re-install ``radish`` again. So, in summary:

``bash cd ~/radish git pull python setup.py install``

*Note: On some systems you have to be root to install a package over setuptools.*

How to use?
-----------

Coming soon ...

Writing tests
-------------

Coming soon ...

Contributing
------------

Coming soon ...

Infos
-----

The files which are currently in the testfiles-folder are from
lettuce - another TDD tool!


