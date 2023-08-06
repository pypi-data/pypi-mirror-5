`pdoc` is a library and a command line program to determine the public 
interface of a Python module or package. The `pdoc` script can be used to 
generate plain text or HTML of a module's public interface, or it can be used 
to run an HTTP server that serves generated HTML for installed modules.

Prominent features include:

* Support for documenting data representation by traversing the abstract syntax 
  to find docstrings for module, class and instance variables.
* For cases where docstrings aren't appropriate (like a
  [namedtuple](http://docs.python.org/2.7/library/collections.html#namedtuple-factory-function-for-tuples-with-named-fields)),
  the special variable `__pdoc__` can be used in your module to
  document any identifier in your public interface.
* Usage is simple. Just write your documentation as Markdown. There are no 
  added special syntax rules.
* `pdoc` respects your `__all__` variable when present.
* When `pdoc` is run as an HTTP server, external linking is supported between 
  packages.
* When available, source code for modules, functions and classes can be viewed 
  in the HTML documentation.
* Inheritance is used when possible to infer docstrings for class members.

`pdoc` has been tested on Python 2.6, 2.7 and 3.3.


Installation
------------
`pdoc` is on PyPI and is installable via `pip`:

    pip install pdoc

Dependencies are [mako](https://pypi.python.org/pypi/Mako) and
[markdown](https://pypi.python.org/pypi/Markdown). (If you're using Python
2.6, then you'll also need [argparse](https://pypi.python.org/pypi/argparse).)

[Pygments](https://pypi.python.org/pypi/Pygments) is an optional dependency. 
When it's installed, source code will have syntax highlighting.


Documentation
-------------
Documentation for the `pdoc` library is available from `pdoc` itself:
[pdoc.burntsushi.net/pdoc](http://pdoc.burntsushi.net/pdoc).


Example usage
-------------
`pdoc` will accept a Python module file, package directory or an import path.
For example, to view the documentation for the `csv` in the console:

    pdoc csv

Or, you could view it by pointing at the file directly:

    pdoc /usr/lib/python2.7/csv.py

Submodules are fine too:

    pdoc multiprocessing.pool

Generate HTML with the `--html` switch:

    pdoc --html csv

A file called `csv.m.html` will be written to the current directory.

Or start an HTTP server that shows documentation for modules found only in your 
`PYTHONPATH` environment variable:

    pdoc --http

Then open your web browser to `http://localhost:8080`. However, you won't be 
able to see documentation for the standard library. To see that, add the
`--http-std-paths` switch.

There are many other options to explore. You can see them all by running:

    pdoc --help


License
-------
It's [in the public domain](http://unlicense.org).


Motivation
----------
At the time of writing, there are three tools available to me to provide 
documentation for my Python packages. Those tools are
[pydoc](http://docs.python.org/2/library/pydoc.html),
[epydoc](http://epydoc.sourceforge.net) and
[sphinx](http://sphinx-doc.org). `pydoc` does not provide facilities for 
documenting data representation and its HTML output is impossible for me to use 
productively. `sphinx` is tool I have been unable to get working despite trying 
and failing several times over the past couple years. More to the point, 
automatic API documentation does not seem to be a primary goal of `sphinx`, 
where prose seems more preferrable. If the documentation for my API is not with 
my source code, then I have no hope of maintaining it.

Finally, `epydoc` is what I had been using for several years. The last release 
was in 2008 and it is not compatible with Python 3. In addition to the web
pages it produces being difficult for me to browse, it is over 25,000 lines
of code. By comparison, `pdoc` is under 3,000 lines of code. (Only 1,500 of
those lines is Python code. The rest is mostly HTML and CSS in Mako templates.)

