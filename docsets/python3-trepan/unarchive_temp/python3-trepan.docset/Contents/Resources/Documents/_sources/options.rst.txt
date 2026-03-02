Command-line Options
====================

The abbreviated forms are shown below with ``-`` and long forms are shown
with  ``--``  to  reflect  how  they  are  shown  in  ``--help``.  However, ``trepan3k``,
and ``trepan3kc`` recognizes all of the following conventions for most options:

* ``--`` *option* ``=`` *value*
* ``--`` *option* *value*
* ``-`` *option* ``=`` *value*
* ``-`` *option* *value*
* ``--`` *o* ``=`` *value*
* ``--`` *o* *value*
* ``-`` *o* ``=`` *value*
* ``-`` *o* *value*

``trepan3k``
------------

``trepan3k`` invokes the debugger. Unless options ``--client`` or
``--server`` is used, the debugger runs entirely in the debugged process.

Although you can enter this debugger without a program to be debugged,
if there is a filename argument given, it indicates the program that
will be run under the debugger.


``--version``
   Show trepan3k's version number and exit.

``-h``, ``--help``
   Show a help message which includes these options and exit.

``-X``, ``--trace``
  Show lines before executing them. This option also sets ``--batch``.

``-F``, ``--fntrace``
  Show functions before executing them.

``--basename``
  In reporting filename, show only the basename. This is useful, for example,
  in regression tests

``--client``
  Connect to an existing debugger process started with the ``--server`` option. See also options ``H`` and ``P``

``-x`` *debugger-command-path*, ``--command=`` *debugger-command-path*
  Execute commands from *debugger-command-path*.

``--cd=`` *directory-path*
  Change current directory to *directory-path*.

``--confirm``
  Confirm potentially dangerous operations.

``--no-confirm``
  Do not confirm potentially dangerous operations.

``--dbg_trepan``
  Allow debugging the debugger.

``--different``
  Consecutive debugger stops should have different positions.

``--edit-mode=`` { ``emacs`` | ``vi`` }
  Set debugger-input edit mode, either "emacs" or "vi", used by GNU
  readline, lineedit, or toolkit-prompt.  The default is
  "emacs". Inside the debugger, you can toggle the edit mode using ESC
  CTRL-j (same as you would in ``gdb``).

``-e`` *debugger-commands-string*, ``--exec=`` *debugger-commands-string*
  List of debugger commands to execute. Separate the commands with ``;;``.

``-H`` *IP-or-hostname*, ``--host=`` *IP-or-hostname*
  Connect to *IP* or hostname. Only valid if ``--client`` option is given.

``--highlight=``{``light`` | ``dark``| ``plain``}
  Use syntax and terminal highlight output. The value ``plain`` indicates no highlighting

``--private``
  Don't register this as a global debugger

``--main``
  First stop should be in ``__main__``

``--no-main``
  First stop should not be in ``__main__``.

``--post-mortem``
  Enter debugger on an uncaught (fatal) exception

``--no-post-mortem``
  Don't enter debugger on an uncaught (fatal) exception


``-n``, ``--nx``
  Don't execute commands found in any initialization files.

``-o`` *path*, ``--output=`` *path*
   Write debugger's output (stdout) to FILE

``-P`` *port-number*, ``--port=`` *port-number*
  Use TCP/IP port number *port-number* for out-of-process connections.

``--server``
   Out-of-process or "headless" server-connection mode.

``--style=`` *pygments-style*
Set output to pygments style; "none" uses 8-color rather than 256-color terminal

``--sigcheck``
  Set to watch for signal handler changes.

``-t`` *target*, ``--target=`` *target*
  Specify a target to connect to. Arguments should be of form, *protocol*:*address*.

`--from_ipython`` Called from inside ipython.

``--annotate=`` *annotate-number*
  Use annotations to work inside GNU Emacs.

``--prompt-toolkit``
  Try using the Python prompt_toolkit module.

``--no-prompt-toolkit``
   Do not use prompt_toolkit.

``--``
   Use this to separate debugger options from any options your
   Python script to be debugged has.



``trepan3kc``
-------------

``trepan3kc`` can be used to connect to an out-of-process or remote process which is in remote-debug TCP/IP mode.

Most of the options below are the same as in the ``trepan3k`` counterpart when the ``--client`` option is given.


``--version``
   Show trepan3k's version number and exit.

``-h``, ``--help``
   Show a help message which includes these options and exit.

``-H`` *IP-or-hostname*, ``--host=`` *IP-or-hostname*
  Connect to *IP* or hostname. Only valid if ``--client`` option is given.

``-P`` *port-number*, ``--port=`` *port-number*
  Use TCP port number *port-number* for out-of-process connections.

``--pid=`` *pid*
  Use process-id *pid* to get FIFO names for out-of-process connections.
