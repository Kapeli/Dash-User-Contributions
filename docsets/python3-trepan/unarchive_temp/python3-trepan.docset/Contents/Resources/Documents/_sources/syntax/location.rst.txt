.. index:: syntax; location
.. _syntax_location:

Syntax for Source-Code Locations
================================

Several commands like "break" and "list" have locations
embedded in them.

A location can be either a *linespec*, an explicit function, or a *module linespec*


Linespec
--------
.. index:: linespec

A linespec has a colon-separated pair of a source-location parameter
and a line number.  A source location is a file path or a module name.

In [*path*:] *linenum* , the line *linenum* in the source file *path*
is indicated. When *path* is omitted, some default value is given; usually it is the *path* associated with the current frame. Or in
list-like commands, it is the *path* that was most recently set; the
most-recently set path starts as the current frame's path.

If *filename* is a relative file name, then Python's `sys.path` items
(which are assumed to be a list of directories) are tried in the order
given. Often, the current working directory or `.` is in that
list. Note that `.` can be set with the  `cd` debugger command.

To specify a path containing non-alphanumeric characters, specifically
blanks (" "), backslashes ("\"), or quotes, there are several
quoting mechanisms one can use. You can enclose the path in single
quotes, double quotes, or triple quotes as you would do in Python

Location Examples
+++++++++++++++++

::

    10                   # line 10 of the most-recently used path
    myfile.py:2          # line 2 of myfile.py, where the directory name is
                         #resolved from `sys.path`
    ./../myfile.py:3     # line 3 of the parent of some directory in `sys.path`
    /tmp/foo.py:4        # line 4 of absolute path /tmp/foo.py
    "foo's.py":1"        # One way to specify a path with a quote
    '''foo's.py"''':2    # Another way to specify a path with a quote
    'c:\foo.bat':1"      # One way to specify a Windows file name,
    '/My Docs/foo.py':1" # One way to specify a path with blanks in it



function()
----------

Specifies the line that the function *function* starts on. This is the
line that contains `def`. We get this information from the Python code
object, in particular the `co_firstlineno` field.
In  contrast to *gdb*, use parentheses at the end of the function name
to indicate this is a function.

You can also specify functions through the values in a Python program
variables or the function indicated in an instance method.

For example, consider this program:

::

    class Foo():
        def food(): return
    f = Foo()
    b = [f.food]
    x = 2

If you are stopped at the last line `x = 2`. You can specify the function `food`
as either of these ways:

::

   Foo.food()
   f.food()
   b[0]()

Although in the last example `b[0]()` the expressions can get a bit
complex, to simplify parsing, we don't allow arbitrary expressions. We
currently allow only alphanumeric symbols as you'd find in valid
Python identifiers along with extra symbols ".", "[", and "]".  This
means `b[i+1]()` would be invalid because it contains "+".  So would
`b["foo"]()`, assuming `b` were a dictionary, because of the quote
symbol.

*Right now, we don't allow line offsets from functions. If the need
arises, we may do so in the future.*

module linespec
---------------

While functions need a closing `()` to indicate their function-ness,
Python module names don't. What we do here is first look up the name
as a file path.  If that's not found, we look up the file as a Python
module name. Modules have to have been imported before it is accepted in
the debugger. However, you can run `eval` (or `autoeval`) to have
Python ``1mport`` the module inside the debugger.

In sum, file names are distinguished from method names purely by
semantic means. However, *gdb* and thus this debugger have no means to
explicitly tag names as a file path or Python module name. We, but not
*gdb*, make a distinction between functions versus modules and file
paths.

Linespec Examples
+++++++++++++++++

::

    os.path:45  # Line 45 of the file that contains os.path
    os:1        # First line of module os
    os          # Invalid! (for now)

Note that the last line is invalid. In contrast to functions, you need
to give line numbers. Also, it is assumed there is no *file*
called `os` in the last example line. Nor a file called `os.path` in
the first example.
