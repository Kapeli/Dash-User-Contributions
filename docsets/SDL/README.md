SDL 2.0 Docset
==============

SDL 2.0 Docset for Dash (http://kapeli.com/dash)

# Information

This is a compilation of the documentation available for the SDL 2.0 library. Please visit http://libsdl.org/
for more information about this project.

The SDL 2.0 library is release under the zlib license; http://www.libsdl.org/license.php

This docset for Dash is compiled by <karl@ninjacontrol.com>

# Generate docset

Pre-requisite: doxygen

1. Download and unpack SDL source, e.g. http://www.libsdl.org/release/SDL2-2.0.3.tar.gz
2. Go to ``include/`` in extracted directory
3. Update ``doxygen`` :


      GENERATE_DOCSET   = YES
      /*...*/
      DISABLE_INDEX     = YES
      /*...*/
      SEARCHENGINE      = NO
      /*...*/
      GENERATE_TREEVIEW = NO

4. Run ``doxygen``
5. Goto generate ``html`` directory
6. Run ``make``
