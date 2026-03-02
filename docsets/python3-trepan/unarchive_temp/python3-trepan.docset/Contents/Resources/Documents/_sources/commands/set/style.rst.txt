.. index:: set; style
.. _set_style:

Set Style
---------
**set style** [*pygments-style*]

Set the pygments style in to use in formatting text for a 256-color terminal.
Note: if your terminal doesn't support 256 colors, you may be better off
using `--highlight=plain` or `--highlight=dark` instead. To turn off styles
use `set style none`.

To list the available pygments styles inside the debugger, omit the style name.


Set Style Examples:
+++++++++++++++++++

::

    set style            # give a list of the style names
    set style colorful   # Pygments 'colorful' style
    set style fdasfda    # Probably display available styles
    set style none       # Turn off style, still use highlight though

.. seealso::

   :ref:`show style <show_style>` and :ref:`set highlight <set_highlight>`
