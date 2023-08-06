Super Zippy
===========

Super Zippy takes a Python package and its pure Python dependencies and transforms them all into a single executable file.

Linux is the only OS supported right now. `The basic strategy <#how-it-works>`_ that Super Zippy uses to create the executable should work for any operating system though, so please `send me an email <http://johnsullivan.name>`_ if you would be interested in helping us test other operating systems.

Examples
--------

Say I'm trying to write a Python script that uses `Clint <https://github.com/kennethreitz/clint>`_ to provide nice console output. I can create a project with a directory tree as below (this example is in the repo under `examples/readme/ <https://github.com/brownhead/superzippy/tree/master/examples/readme/>`_).

.. code-block::

    + setup.py
    + tinyscript/
    |   + __init__.py
    |   + main.py

The ``setup.py`` file establishes the Clint dependency and is very short. This file must exist because Super Zippy will use `pip <http://www.pip-installer.org/>`_ to install your package, and pip needs this file.

.. code-block:: python

    # setup.py
    from setuptools import setup, find_packages
    setup(
        name = "tinyscript",
        packages = find_packages()
    )

The ``__init__.py`` file is empty (see `here <http://stackoverflow.com/questions/448271/what-is-init-py-for>`_ for info).

Finally, the ``main.py`` file has our actual script.

.. code-block:: python

    # main.py
    import sys

    def foo():
        print "I am a mighty foo function!"
        sys.exit(0)

    def bar():
        print "Nice to meet you, I am bar."
        sys.exit(1)

    if __name__ == "__main__":
        print "Running as a script!"
        sys.exit(2)

We can now use Super Zippy.

.. code-block:: shell

    $ ls
    setup.py tinyscript/
    $ superzippy . tinyscript.main:foo
    $ ls
    setup.py tinyscript/ tinyscript.sz
    $ ./tinyscript.sz
    I am a mighty foo function!
    $ echo $?
    0

If we'd like to have the ``bar()`` function be our entry point (rather than the ``foo()`` function above), we could run

.. code-block:: shell

    $ superzippy . tinyscript.main:bar
    $ ./tinyscript.sz
    Nice to meet you, I am bar.
    $ echo $?
    1

There's a number of options you can give Super Zippy and you can get an up-to-date listing of them by running ``superzippy -h``.

Installing
----------

You can install Super Zippy from pip easily (`see here for installing pip <http://www.pip-installer.org/en/latest/installing.html>`_). This will grab the latest stable release.

.. code-block:: shell

    $ pip install superzippy

Alternatively, you can install the most recent version off of GitHub.

.. code-block:: shell

    $ git clone https://github.com/brownhead/superzippy.git
    $ cd superzippy/
    $ pip install .

If you are planning to do development on Super Zippy, you may want to install Super Zippy in `editable mode <http://pythonhosted.org/distribute/setuptools.html#development-mode>`_. You can do this by adding the ``-e`` flag to pip above to get ``pip install -e .``.

You can of course also use Super Zippy on itself to make a Super Zip of Super Zippy. Though doing this automatically may be done in the future, it seems mostly unecessary at the moment to add this into our release process.

How it Works
------------

Super Zippy's algorithm is fairly straightforward.

1. Create a virtual environment using `virtualenv <http://www.virtualenv.org/>`_.
#. Install all the desired packages into the virtual environment using `pip <http://www.pip-installer.org/>`_.
#. Grab the site-packages directory out from the virtual environment (which is the directory that contains all installed packages) and put it in an empty temporary directory.
#. Add a `__main__.py <http://stackoverflow.com/questions/4042905/what-is-main-py>`_ file to the temporary directory that executes the desired function.
#. Zip the temporary directory up.
#. Make the zip file executable by flipping the executable bit and adding ``#!/usr/bin/env python`` to the beginning of the file.

Who Made This?
--------------

My name is `John Sullivan <http://johnsullivan.name>`_ and I created this over a couple weekends with the assistance of `Chris Manghane <https://github.com/paranoiacblack>`_. After the initial release, `Steven Myint <https://github.com/myint>`_ graciously submitted several useful patches as well.

If you are interested in helping with the development, feel free to fork and dive in! If you'd just like to send me a message you can find my contact information on my portfolio at `johnsullivan.name <http://johnsullivan.name>`_.

License
-------

Apache License v2.0 (see `LICENSE <https://github.com/brownhead/superzippy/blob/master/LICENSE>`_ for full text).

If you need a more permissive license please `open up an issue in the tracker <https://github.com/brownhead/superzippy/issues>`_ that describes your desired use case.
