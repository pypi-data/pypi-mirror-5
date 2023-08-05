PyGenCAD (read pidgin-CAD)
==========================
:Description: Python module for generating CAD software command scripts.
:License: BSD-style, see `LICENSE.txt`_
:Author: Ed Blake <kitsu.eb@gmail.com>
:Date: Jun. 19 2013

.. include:: ../hglog.rst

Introduction
------------
A pidgin, or pidgin language, is a simplified language that develops as a means
of communication between two or more groups that do not have a language in
common. It is most commonly employed in situations such as trade, or where both
groups speak languages different from the language of the country in which they
reside (but where there is no common language between the groups). (Via Wikipedia_)

This module provides a simple interface to generate command scripts targeting
various CAD software via Python. Low level methods are provided for inputting
raw commands, single and multiple coordinate input, and setting the active
layer/level. Convenience methods are also provided for drawing lines,
polylines, circles, and text. Methods are also provided for storing element
references and moving, copying, rotating, scaling, and erasing elements by
reference.

A uniform interface is provided across all supported backends allowing one
Python script to output to multiple platforms using identical code. Additional
backend specific features may be available, and arbitrary code can be generated
using the 'cmd' method.

Requirements
------------
This is a pure Python module with no external dependencies (except a supported
backend to execute your output).

The module was written and tested against Python2.7_ and is using several
non-backward compatible features: 

    * Non-indexed string format placeholders `{}`
    * Chained context managers
    * Extended unittest asserts

Adding Python >= 3.0 support should be trivial, but I am not currently using
Python 3 anywhere.

Installation
------------
Download the repo archive, unzip, and run `python setup.py install` in the
unzipped directory.

Alternately use pip to get the latest version uploaded to PyPI 
`pip install pygencad`.

Testing
-------
A helper script "runtests.py" is provided in the project root to run the entire 
test suite. Runnable test scripts are provided for each sub-module in the test 
folder.

Additionally the cover_tests.py script will run all the tests using coverage.py,
with branch coverage, and open the html report.

Also running build_docs.py will run doctests as part of the sphinx build.

Usage
-----
Importing the pygencad module brings in a named module for each backend,
a dict of name:backend pairs and name:ext pairs, and two helper functions.
In normal usage you would call the get_script function with a filelike and 
the name of your desired backend to get started::

    import pygencad as pgc

    # Notice you are responsible for the life of your filelike
    filename = 'outfile' + pgc.backext['autocad']
    with open(filename, 'w') as outfile:
        # Script objects handle context setup and teardown
        with pgc.get_script(outfile, 'autocad') as script:
            script.cmd("pass")

The other helper function returns a new layer object for the current backend::
    
    my_layer = pgc.get_layer('autocad')('mylayer', co=1)

Instantiated script objects also have a reference to their Layer class::

    my_layer = script.Layer('mylayer', co=1)

The script object also provides a layer context manager::

    with script.layer(my_layer):
        # Draw circle on my layer
        script.circle((0,0), 5)
    # The layer method creates a new layer if passed layer params
    with script.layer('extra', co=2):
        script.line((-2.5,-2.5), (2.5, 2.5))

After you're script has run you should get a script you can run with you're
backend of choice. AutoCAD scripts are run by using the *script* command, or by
dragging the script file onto the AutoCAD window. MicroStation scripts are run
by typing *@* followed by the DOS short name path to you're script in the keyin
editor. SVG output is just bare <svg> tags, Wrapping in a minimal HTML document
is recomended.

See the specific backend modules in the docs_ for more info.

ToDo
----
* Add support for setting element overrides globally and per method call.
* Write cool examples, both general and backend specific.
* Add a mirror modification method and/or implement non-uniform scaling.
* Add AutoCAD point mode support.
* Add some more AutoLisp utility code to the autocad module.
* Move block/cell code to base class (name?). (SVG use defs and links as blocks)
* Improve MicroStation specific methods.
* Add support for more backends:
    * Blender
    * VPython
    * ???


.. _Wikipedia: http://en.wikipedia.org/wiki/Pidgin
.. _LICENSE.txt: https://bitbucket.org/kitsu/pygencad/src/tip/LICENSE.txt
.. _Python2.7: http://python.org/download/releases/2.7.3/#download 
.. _Docs: https://pygencad.readthedocs.org
