.. index:: set; patsub
.. _set_patsub:

Set Substitution Pattern
------------------------

**set patsub** *from-re* *replace-string*

Add a substitution pattern rule replacing *patsub* with
*replace-string* anywhere it is found in source file names.  If a
substitution rule was previously set for *from-re*, the old rule is
replaced by the new one.

In the following example, suppose in a docker container /mnt/project is
the mount-point for /home/rocky/project. You are running the code
from the docker container, but debugging this from outside of that.


Set Substitution Pattern Example:
+++++++++++++++++++++++++++++++++

::

    set patsub ^/mmt/project /home/rocky/project

.. seealso::

   :ref:`set substitute <set_substitute>`
