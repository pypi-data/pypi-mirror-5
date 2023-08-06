quickunit
=========

Given standard test setup, will determine which tests need to run against a given diff.

For example, say you're working in your branch called my-new-sexy-feature, which modifies the following files:

::

    src/foo/bar/__init__.py
    src/foo/bar/baz.py
    src/foo/biz.py

If you're using a traditional test layout, we'll automatically add the following rule for you:

::

    tests/{path}/test_{filename}

Otherwise you can add rules using regular expression syntax in combination with the path and filename formatters.

Now if we run with the default options, ``nosetests --with-quickunit``, it will look for tests (by default) in
the following base directories:

::

    tests/src/foo/bar/test_baz.py
    tests/src/foo/test_biz.py

(It does this by analyzing the diff against master, and determining which files you've changed
are tests, including them, and which files containing test coverage in a parallel directory.)

Config
------

If you want to support multiple directories for searching (let's say you break up unittests from integration tests)
you can do that as well:

::
    --quickunit-rule=tests/{path}/test_{filename} --quickunit-rule=tests/{path}/{basename}/tests.py

Or, if you'd prefer, via ``setup.cfg``:

::

    quickunit-rule = tests/{path}/test_{filename}
                     tests/{path}/{basename}/tests.py

Rules
-----

Rules are a combination of simple formatting a regular expressions.

The following formatted variables are available within a rule:

{path}
  The base path of the filename (e.g. foo/bar)
{filename}
  The filename excluding the path (e.g. baz.py)
{basename}
  The filename excluding the extension (e.g. baz)

A rule is first formatted (using ``.format(params)``) and then compiled into a regular expression on top of each changed file.
