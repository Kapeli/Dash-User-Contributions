Box2D Docset
==============

Box2D Docset for Dash (http://kapeli.com/dash)

# Information

This is a compilation of the documentation available for the Box2D library. Please visit http://box2d.org/
for more information about this project.

Box2D is developed by Erin Catto and released under the zlib license.


This docset for Dash is compiled by <karl@ninjacontrol.com>

# Generate docset

Pre-requisite: doxygen

1. Download and unpack Box2D source (https://code.google.com/p/box2d/downloads/list)
2. Go to ``Box2D_v2.3.0/Box2D/Documentation/API/html/`` in extracted directory
3. Update ``Doxyfile`` :

```
  GENERATE_DOCSET   = YES
  /*...*/
  DISABLE_INDEX     = YES
  /*...*/
  SEARCHENGINE      = NO
  /*...*/
  GENERATE_TREEVIEW = NO
  /*...*/
  DOCSET_BUNDLE_ID  = org.box2d
```
4. Run ``doxygen``
5. Goto generate ``html`` directory
6. Run ``make``
7. Docset is generated as ``org.box2d.docset`` in current directory
