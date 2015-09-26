Eigen 3.2.4 Docset
==================

Eigen 3.2.4 Docset for Dash (http://kapeli.com/dash)

# Information

This is a compilation of the documentation available for the Eigen 3.2.4 library.
Please visit http://eigen.tuxfamily.org/ for more information about this project.

The Eigen 3.2.4 library is Free Software. It is licenced under the [MPL2]
(http://www.mozilla.org/MPL/2.0), which is a simple weak copyleft license.

Note that currently, a few features rely on third-party code licensed under the
LGPL: SimplicialCholesky, AMD ordering, and constrained_cg. Such features can be
explicitly disabled by compiling with the EIGEN_MPL2_ONLY preprocessor symbol
defined. Furthermore, Eigen provides interface classes for various third-party
libraries (usually recognizable by the <Eigen/*Support> header name). Of course
you have to mind the license of the so-included library when using them.

This docset for Dash is compiled by [Egor Larionov](https://github.com/elrnv)
This docset for Dash is recompiled by [Zuogong Yue](https://github.com/oracleyue), with LaTeX enabled to fix formula pictures.

# Generate docset

Pre-requisites: doxygen, cmake

1. Download and unpack Eigen source, e.g. http://bitbucket.org/eigen/eigen/get/3.2.4.tar.gz
2. Make a new directory called ``build/`` in extracted directory
3. Go to the newly created directory and run ``cmake ../.``
4. Go to the ``doc/`` directory
5. Update ``Doxyfile`` :

``
      DOCSET_BUNDLE_ID  = eigen
      /*...*/
      GENERATE_DOCSET   = YES
      /*...*/
      DISABLE_INDEX     = YES
      /*...*/
      SEARCHENGINE      = NO
      /*...*/
      GENERATE_TREEVIEW = NO
``

6. Run ``make``
7. Goto generated ``html`` directory
8. Run ``make``
