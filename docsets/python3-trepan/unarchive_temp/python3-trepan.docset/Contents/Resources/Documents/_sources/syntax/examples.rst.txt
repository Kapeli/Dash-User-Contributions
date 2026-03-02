Command examples
================

::

        # This line does nothing. It is a comment. Useful in debugger command files.
        # This line also does nothing.
        s    # by default, this is an alias for the "step" command
        info program;;list # error no command 'program;;list'
        info program ;; list # Runs two commands "info program" and "list"

.. seealso::

 :ref:`macro <macro>`, :ref:`alias <alias>`, :ref:`python <python>`, :ref:`set auto eval <set_autoeval>`, :ref:`info macro <info_macro>`, and the *show* variants of the above *set* commands.
