What is it?
===========

``pyzzer`` is a simple tool for creating Python-runnable zip archives from Python package and module sources. It uses Python's standard library ``zipfile`` module to construct runnable .zip files. There are several elements to making archives runnable:

* They need a `shebang line <https://en.wikipedia.org/wiki/Shebang_(Unix)>`_ which indicates to POSIX shells the native executable that is used to run them. Archives created by ``pyzzer`` have a shebang line prepended to them, which is ``#! /usr/bin/env python`` by default but can be overridden with a command-line argument to ``pyzzer``.

* On POSIX systems, the executable bit should be set in the archive's file-system attributes. This is set by ``pyzzer`` for the current user.

* For Python to be able to run a .zip archive, the archive needs to contain a "main" module named   ``__main__.py``. For ``pyzzer``-created archives, you can either specify an existing ``__main__.py`` file, specifying only a single source file (which then is written to the archive as ``__main__.py``) or have ``pyzzer`` make one from a module:callable combination. An archive cannot be created with ``pyzzer`` unless it contains a top-level ``__main__.py``.

Windows support
===============

On Windows, the recommended way of running archives is to have the
`Python Launcher for Windows <https://bitbucket.org/pypa/pylauncher/downloads>`_ installed and to
use that to run archives. The launcher processes POSIX-style shebang lines and is included in
Python 3.3 and later, but the standalone launcher receives updates more frequently. While the
Python 3.3 launcher only recognises ``.py``, ``.pyc``, ``.pyo`` and ``.pyw`` extensions, the
standalone launcher also recognises ``.pyz`` and ``.pyzw`` extensions, which are used for
runnable archives.

It *is* possible to have ``pyzzer`` provide the ability to prepend archives with a suitable
native Windows executable which is capable of launching archives appended to it. Such launchers
are available for 32- and 64-bit console and Windows applications (they are developed in a
`separate project <https://bitbucket.org/vinay.sajip/simple_launcher>`_). Since including these
executables in ``pyzzer`` makes it larger, this support is provided in a separate download (see `Getting pyzzer`_).

Usage
=====

The usage message gives the available options::

    Usage: pyzzer [options] DIR_OR_FILE_OR_ARCHIVE [DIR_OR_FILE ...]

    Convert Python source directories and files to runnable zip files. The
    first argument can be an existing archive, which can be added to with
    additional sources.

    Options:
      -h, --help      show this help message and exit
      -s SHEBANG      Specify a shebang line to prepend to the archive, or the
                      path to an interpreter which can be used to determine the
                      shebang line to use. Defaults to "#! /usr/bin/env python"
                      on POSIX and to the value of sys.executable on Windows.
      -m MODULE:ATTR  Specify a callable which is the main entry point.
      -x REGEX        Specify regexes to exclude from the zip  (can specify more
                      than once).
      -o FILENAME     Specify the path of the file to write to. If not specified
                      and a source archive is given, it will be used; otherwise
                      the extension defaults to .pyz and the name defaults to
                      the first directory or file specified.
      -v              Provide information about progress.
      -i              Inspect an existing archive.
      -l LAUNCHER     Specify a Windows launcher to use (t32/w32/t64/w64).*
      -r              Recurse package directories.

\* Only available with the ``pyzzerw.pyz`` variant (see `Getting pyzzer`_).

The following sections discuss the options in more detail.

Positional arguments
--------------------

The positional arguments are an optional existing archive to add to, followed by a list of directories and files. These are processed as follows:

* If the first argument is an archive, any shebang it contains will be preserved unless ``-s`` is used to override it. The contents of the archive are added to with the sources specified in the rest of the command line. Any file contents before the archive/shebang (such as a native executable launcher on Windows) are preserved unless ``-l`` is available and used.

* If an argument is a file, it is archived as a top-level file.

* If an argument is a directory,``pyzzer`` determines whether it is a package according to whether it contains an ``__init__.py``. If it does, it is treated as a Python package and its contents are written to the archive as a directory. By default, sub-packages are not archived unless you specify ``-r``, in which case all sub-packages are archived. If the directory is not a package, its contents will be archived as top-level files and no recursion into sub-directories will be performed.

* If any files are added which already exist in the archive, an error will be raised.

Before adding to an archive, files in directories will be checked against any exclusion patterns specified using ``-x`` and excluded if they match. In addition, files ``.hgignore``, ``.gitignore`` and ``.bzrignore`` are never added, and directories ``.hg``, ``.git``, ``.bzr`` and ``.svn`` are never recursed into even when ``-r`` is specified. Any files not specifically excluded will be included in the archive on the assumption that they are package data. Any files specified in the command line are assumed to be wanted and are not checked against any exclusion patterns.

Setting the shebang line
------------------------

You can use the ``-s`` argument to specify the shebang line to use. If the argument value does not begin with a ``#!``, it will be prepended to the specified value -- so you can just specify the path to an interpreter, as that's all that's needed.

Specifying a main program
-------------------------

You can specify an existing function somewhere in the archived source files as the main function called by Python when it runs an archive, by using the ``-m`` argument with a module:callable argument such as ``foo:main`` or ``foo.bar:baz.main``. When you do this, ``pyzzer`` wraps a call to this function in a Python source file which is saved as a top-level ``__main__.py`` in the archive. If you do this, you must not specify a ``__main__.py`` file in your sources. If you don't specify ``-m``, there must be a top-level ``__main__.py`` file specified in the sources you add to the archive.

Excluding files from an archive
-------------------------------

You can specify one or more regular expressions which indicate that files with names matching them should be excluded from the archiving. The matches are done using ``search``, which means that you need to specify ``^`` and ``$`` explicitly to anchor matches. If any pattern matches a file name, that file is skipped. Note that patterns are passed as is to the regular expression compiler, so take care to quote and/or escape any special characters in the pattern.

Specifying the output archive name
----------------------------------

You can specify a name for the output archive using the ``-o`` argument. If not specified and an archive was passed as the first argument, the same archive will be overwritten. If the first argument is not an archive, its file name is used as the output archive name, and ``.pyz`` is used as the extension.

Getting feedback on progress
----------------------------

If the ``-v`` option is specified, ``pyzzer`` will print to the console the relative names of files as it writes them to the archive.

Examining an existing archive
-----------------------------

If the ``-i`` argument is specified, the first positional argument should be an existing archive and subsequent positional arguments are ignored. The existing archive's shebang line and contents are printed. If a native executable launcher is detected, that is indicated in the output.

Recursing over sub-packages
----------------------------

To recursively add sub-packages in a package, specify the ``-r`` argument. When recursing, all directories below a package are assumed to be sub-packages or data.

Specifying a Windows launcher
-----------------------------

Though it is preferred that Windows support is through the Python Launcher for Windows, the ``pyzzerw.pyz`` archive allows stock native executables to be prepended to the archive. To use them, specify ``-l``  with one of ``t32``, ``w32``, ``t64`` or ``w64`` where the numeric suffix indicates whether a 32-bit or a 64-bit launcher is used, and the initial letter is interpreted as ``t`` for text (i.e. console) applications, and ``w`` for Windows application. You should also specify ``-o`` with a filename with a ``.exe`` extension.

In theory, you should be able to launch  32-bit or 64-bit Python interpreters from a 32-bit launcher. However, 64-bit launchers have been provided in case of problems.

Note that for best effect, any shebang you specify should match the launcher used (e.g. ``w32`` or ``w64`` would be used with a shebang specifying the path to a ``pythonw.exe``). Otherwise, you may see spurious console windows (windowed application run with a ``python.exe``) or no output at all (console application run with a ``pythonw.exe``).

These launchers know how to process an archive appended to them. When the main program in the archive is run,
``sys.argv[0]`` will specify the name of the executable archive (``something.exe``).

The launchers have embedded manifests, which should mean that you won't get UAC prompts.

Running programs in runnable archives
-------------------------------------

You should just be able to run runnable archives like any normal Python script, by specifying the archive name as the command and any arguments to be passed to the script as arguments to the command.

Getting pyzzer
==============

There are two variants available. The `pyzzer.pyz <https://bitbucket.org/vinay.sajip/pyzzer/downloads/pyzzer.pyz>`_ download doesn't include support for native Windows launchers, whereas the `pyzzerw.pyz <https://bitbucket.org/vinay.sajip/pyzzer/downloads/pyzzerw.pyz>`_ download does. Note that both of these are console applications on Windows.

How pyzzer was built
====================

Naturally, ``pyzzer`` was used to build executable archives containing itself. The command line for building ``pyzzer.pyz`` is::

    python -m pyzzer -o pyzzer.pyz -x "exe|__main__|lau" -m pyzzer:main pyzzer

and that for ``pyzzerw.pyz`` is::

    python -m pyzzer -o pyzzerw.pyz -x "exe|__main__" -m pyzzer:main pyzzer

These commands were run from the ``pyzzer`` project directory (above the ``pyzzer`` package directory). The ``pyzzer.launchers`` module, which contains the extended Windows launcher functionality and enables the ``-l`` option, is excluded from the first build.

Testing pyzzer
==============

To run the test suite for ``pyzzer``, you need to clone the repository, and then build ``pyzzer.pyz`` and ``pyzzerw.pyz`` using the commands shown above. After this, you can run the ``test_pyzzer.py`` script. The tests are run using ``subprocess`` to invoke the built files with various command line options.

Acknowledgements
================

Many thanks to Paul Moore for helpful suggestions about how to improve ``pyzzer``.

Limitations
===========

* There is no byte-compilation support at present.
* No checks are made to verify that a specified ``-m`` value actually exists in the sources.
* Packages are recognised by the existence of an ``__init__.py__``, so there is no recognition of new-style namespace packages (which have no such file).
* Replacing files in existing archives is not supported.

Patches are welcome to help remove or mitigate these limitations.

Other resources
===============

* `PEP 441 <http://www.python.org/dev/peps/pep-0441/>`_ is the PEP advocating added support for ``.pyz`` and ``.pyzw`` archives.
* Daniel Holth's `pyzaa package <https://bitbucket.org/dholth/pyzaa>`_ provides similar functionality to ``pyzzer``.
* You don't *need* to install ``pyzzer`` using ``pip`` (it's a one-file executable, after all) - but if you absolutely must, here it is `on PyPI <https://pypi.python.org/pypi/pyzzer>`_.

Change log
==========

0.1.1
-----

Released: 2013-08-23.

- Fixed ``TypeError`` in Python 3.x.

- Made the default shebang use ``sys.executable`` on Windows when ``-l`` is specified, rather than ``/usr/bin/env python`` which is used on POSIX (and also Windows where the Python Launcher is used).

- If the output extension is ``.exe`` and no launcher has been specified, ``t32`` will be assumed except on 64-bit Windows (where ``t64`` will be assumed).

- If only a single source file is specified, and no ``-m`` option is given, and the archive contains no other files, then the single file is written to the archive with name ``__main__.py``.

- Added tests.

- Tweaked help messages.

- Removed unused code.

- Moved change log to the README and updated documentation.

0.1.0
-----

Released: 2013-08-19

- Initial release.
