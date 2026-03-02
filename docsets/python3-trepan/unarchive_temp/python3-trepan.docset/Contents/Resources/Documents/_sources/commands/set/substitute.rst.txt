.. index:: set; substitute
.. _set_substitute:

Set Substitute
--------------
**set substitute** *from-name* *to-path*

Add a substitution rule replacing *from-name* into *to-path* in source file names.
If a substitution rule was previously set for *from-name*, the old rule
is replaced by the new one.

Spaces in "filenames" like `<frozen importlib._bootstrap>` messes up our normal shell
tokenization, so we have added a hack to ignore `<frozen .. >`.

So, for frozen files like `<frozen importlib._bootstrap>`, use `importlib._bootstrap`

Set Substitute Examples:
++++++++++++++++++++++++

::

    set substitute importlib._bootstrap /usr/lib/python3.4/importlib/_bootstrap.py
    set substitute ./gcd.py /tmp/gcd.py
