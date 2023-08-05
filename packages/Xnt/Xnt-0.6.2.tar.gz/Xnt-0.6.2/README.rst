.. # vim: colorcolumn=70:textwidth=69:syntax=rst:

===
Xnt
===

A wrapper build tool

Release Notes
=============

0.6.2:2013-06-26
----------------

* Add `nvcc` wrapper to `xnt.build.make`

* `xnt.build.make.*` `target` is now required

* Update Documentation

  * Fix autodoc issues

  * Add/ Update Better dependencies section

0.6.1:2013-03-23
----------------

* Add Parameter Passing to `xnt.build.make`

* Suppress Noisy LaTeX Output

* Update Documentation

0.6.0:2013-03-10
----------------

* pylint ALL THE THINGS

  * `properties` is now `PROPERTIES` for build files

* Fix `xntcall` function

* Rewrite Parser/Parsing (again)

  * Like last time, this changes the options again (see below or
    documentation)

* Add option for build file specification

* Add LaTeX Build Module

0.5.1:2013-03-02
----------------

* Promote to Beta Status

* Internal Refactoring

  * Versioning

* Minor Documentation Changes

0.5.0:2013-02-21
----------------

* Rewrite Command Parsing

  * This change does incur some interface change. Namely,
    ``--version`` is now ``version``, ``--usage`` is now ``help``
  * All other commands and switches are the same
  * See `Package Documentation`_ for more information

* Rework Return Values

  * Silently succeed, loudly fail (quickly)

0.4.1:2013-01-25
----------------

* Add Multi Target Execution

* Add Optional Flags to (Sub)Build modules (make)

* Add Exit Code Return

0.4.0:2013-01-21
----------------

* Moved to GitHub!

* Add Parameter Passing to Xnt

* Combined Build Modules ((N)Ant and make all live in
  ``xnt.build.make``)

* Add Compiler Wrappers (gcc/g++ and javac)

Testing
-------

I don't test everything as well as maybe I would like and, of course,
some better integration tests would help. But one area that is
seriously lacking testing are the Windows builds. I don't have the
best access to a Windows box and so I may not notice a potentially
huge bug for some time.

Motivation
==========

When writing something such as a build tool, there is always the
question: "why?". Why write yet another build tool?

Well, there are several reasons that are the backing motivation:

First, developing a variety of software, using one and only one build
tool for every project is nearly (if not entirely) impossible. There
is a desire to have a consistent build step and process when testing
and deploying. Given the environment in which the code is written is
heterogeneous, having one uniform build tool that wraps itself around
the other ones (and has the ability to expand to new ones) is ideal.

Second, short of dropping into the language the build tool was
written in, expanding some build steps is very difficult (or at least
can be). Further there can be complicated build targets that require
some interesting and potentially involved (smelly) procedures to be
accomplished, that may or may not be easy to describe in the build
file or in the native language. Therefore, having a wrapping build
framework/ tool that is written in an easy to read and write
language, such as Python, these complicated steps can depend less on
some funky new build library (further adding to the dependency tree)
and can become just implementation details (assuming, of course, you
buy into Xnt first).

Last, and most certainly the least, I wanted to explore the idea. I
wanted to write something that made me think about solving some of
the problems challenged by such a tool.

What Xnt Is NOT
===============

Calling Xnt simply a build tool is (grossly?) misleading. Xnt is not
really a build tool in the traditional sense. Like stated above, it
is more a wrapper around existing build tools. I didn't want to
replace what some of these tools already do really well (e.g. being
able to describe how to compile an entire large Java program in
several lines of code using Ant).

What Xnt IS
===========

Xnt is a wrapping build tool, intended to be used with a multitude of
sub-build tools, even in the same project. Regardless of the language
the project is written in, Xnt should be able to suite your needs. If
your language's build tool is unable to do something concisely or
cleanly, Python should help. [There could be more here... I can't
think of it though.]

Installing and Setting Up Xnt
=============================

Using Xnt is fairly simple. All you will need to do is install it,
create a ``build.py`` file for your project, and invoke it just like
any other build tool you have used before (e.g. ``$ xnt {target}``).

Dependencies
------------

There are a few required and optional dependencies to install and run
Xnt. Namely, reference the following list:

* ``distribute``
* ``Ant`` (Optional)
* ``CVS`` (Optional)
* ``Git`` (Optional)
* ``LaTeX`` (Optional)
* ``Make`` (Optional)
* ``Mercurial`` (Optional)
* ``NAnt`` (Optional)

For developers, there are a few more dependencies.

* ``sphinx``
* ``pylint``

Source Install
--------------

To install from source, you can download the source tarball or zip
file (from either `Downloads`_ or `Xnt`_), unpack it into a
temporary directory and then, from a shell or command prompt, run::

    $ python[2] setup.py install [--user]

PyPi/ Pip
---------

To install from PyPi_, you will need `pip`_. Once you have ``pip``,
you may only run::

    $ pip[2] install Xnt [--user]

Linux/ Unix
-----------

If you install using the ``--user`` option in either source or PyPi
installs you may need to add ``~/.local/bin/`` to your ``PATH``
environment variable.

Otherwise, you shall need do nothing more.

Windows
-------

If on Windows, after installing you will need edit your ``PATH``
environment variable to include the ``<python_install_dir>\Scripts``
folder. After which, you will be all set to use Xnt.

Example ``build.py``
====================

Here is a simple ``build.py``::

    #!/usr/bin/env python

    import xnt
    from xnt.build import make

    @xnt.target
    def init():
        xnt.mkdir("bin")

    @xnt.target
    def build():
        init()
        make.ant("build")

    @xnt.target
    def clean():
        xnt.rm("bin")

    @xnt.target
    def rebuild():
        clean()
        build()

    @xnt.target
    def package():
        rebuild()
        xnt.create_zip("bin", "packaged.zip")

    @xnt.target
    def default():
        package()

As you can see, it really just is a Python script. There really isn't
anything really special happening. We just import some of the Xnt
modules, and define some targets. When you call ``xnt``, it will be
loading this script and call the target specified by ``{target}`` or,
if you don't specify one, it will call the target named ``default``.

Usage
=====

Command Usage:

    $ xnt [options] [target]*

Where ``[options]`` are of the following:

* ``-v`` or ``--verbose``: verbose, turn on logging

* ``-b BUILDFILE`` or ``--build-file BUILDFILE``: Specify build file
  for Xnt to load

And where ``[target]*`` are any target(s) method in your ``build.py``
file or, if no target is given, Xnt will attempt to call ``default``.

Other Commands
--------------

* ``-l`` or ``--list-targets``: Xnt will print all targets marked by
  the ``@target`` decorator and possibly their docstrings if they are
  defined

* ``--version``: Print the current version of Xnt and quit

* ``-h`` or ``--help``: Print summary information about Xnt and
  command usage

For more information about Xnt and the built in functions, see the
`Package Documentation`_.

Issues
======

If you find any issues or would like to request a feature, please
visit `Issues`_.

.. _PyPi: http://pypi.python.org/pypi
.. _Package Documentation: http://pythonhosted.org/Xnt
.. _pip: http://www.pip-installer.org/en/latest/installing.html
.. _Downloads: https://github.com/devnulltao/Xnt/archive/master.zip
.. _Xnt: http://pypi.python.org/pypi/Xnt
.. _Issues: https://github.com/devnulltao/Xnt/issues
