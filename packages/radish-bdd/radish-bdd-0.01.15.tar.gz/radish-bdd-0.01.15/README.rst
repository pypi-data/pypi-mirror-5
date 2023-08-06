radish
======

    ``radish`` is a "Behavior-Driven Developement"-Tool written in
    python Version: 0.01.15

--------------

**Author:** Timo Furrer tuxtimo@gmail.com **License:** GPL **Version:**
0.01.15

Table of contents
-----------------

1. `What is radish <#whatis>`_
2. `Installation <#installation>`_

   1. `Simple installation with pip <#installation_pip>`_
   2. `Manual installation from source <#installation_source>`_
   3. `Update source installation <#installation_update>`_

3. `How to use? <#usage>`_
4. `Writing tests <#write_tests>`_
5. `Contribution <#contribution>`_
6. `Infos <#infos>`_

What is ``radish`` ?
--------------------

``radish`` is a "Behavior-Driven Developement"-Tool written in python.
It is inspired by other ``BDD``-Tools like ``cucumber`` or ``lettuce``.

`[⬆] <#TOC>`_

Installation
------------

There are several ways to install ``radish`` on your computer:

`[⬆] <#TOC>`_

Simple installation with pip
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is probably the simplest way to install ``radish``. Since the
``radish`` releases are hostet as well on
`pip <https://pypi.python.org/pypi/pip>`_ you can use the following
command to install ``radish``:

::

    pip install radish

*Note: On some systems you have to be root to install a package over
pip.*

`[⬆] <#TOC>`_

Manual installation from source
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you always want to be up to date with the newest commits you may want
to install ``radish`` directly from `source
code <https://github.com/timofurrer/radish>`_. Use the following command
sequence to clone the repository from github and install ``radish``
afterwards:

::

    git clone https://github.com/timofurrer/radish.git ~/radish
    cd ~/radish
    git submodule init
    git submodule update
    python setup.py install

*Note: On some systems you have to be root to install a package over
setuptools.*

`[⬆] <#TOC>`_

Update source installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have once installation ``radish`` from source you might want to
update it from time to time. Change into the directory where you have
cloned ``radish`` into (default: ``~/radish``) and pull the newest
commit from github. When you've done this you need to re-install
``radish`` again. So, in summary:

::

    cd ~/radish
    git pull
    python setup.py install

*Note: On some systems you have to be root to install a package over
setuptools.*

`[⬆] <#TOC>`_

How to use?
-----------

Coming soon ...

`[⬆] <#TOC>`_

Writing tests
-------------

Coming soon ...

`[⬆] <#TOC>`_

Contribution
------------

 Use virtualenv
~~~~~~~~~~~~~~~

I recommend you to develop ``radish`` in a virtualenv, because than you
can easily manage all the requirements.

::

    virtualenv radish-env --no-site-packages
    . radish-env/bin/active
    pip install -r requirements.txt

More coming soon ...

`[⬆] <#TOC>`_

Infos
-----

The files which are currently in the testfiles-folder are from lettuce -
another TDD tool!

`[⬆] <#TOC>`_
