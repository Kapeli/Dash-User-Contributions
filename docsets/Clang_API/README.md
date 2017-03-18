Clang C++ API Docset
====================

[Clang][clang] is a compiler front end for the programming languages C, C++,
Objective-C, Objective-C++, OpenMP, OpenCL, and CUDA. It uses [LLVM][llvm]
as its back end.

Docset Maintainer
-----------------

**Name**: Lei Zhang

**GitHub**: https://github.com/antiagainst

How to Generate
---------------

```sh
# Download LLVM and Clang source code
cd llvm/

# Configure
mkdir build-doc/
cd build-doc/
cmake -GNinja -DLLVM_ENABLE_DOXYGEN=ON ..

# Change doxygen.cfg for clang in tools/clang/docs/ to make sure that
#   HTML_TIMESTAMP = NO
#   GENERATE_DOCSET = YES
#   DISABLE_INDEX = YES
#   HAS_DOT = YES
#   DOT_PATH = ...

# Build
ninja doxygen-clang
cd tools/clang/docs/doxygen/html/
make -j`sysctl -n hw.ncpu` # Takes serveral hours to finish

mv org.doxygen.Project.docset/ ClangAPI.docset

# Add additional information
cp /path/to/this/repo/resources/icon.png    ClangAPI.docset/
cp /path/to/this/repo/resources/icon@2x.png ClangAPI.docset/Contents/Resources/Documents/
cp /path/to/this/repo/resources/Info.plist  ClangAPI.docset/Contents/

# Make tarball
tar --exclude='.DS_Store' -cvzf ClangAPI.tgz ClangAPI.docset
```

[clang]: https://clang.llvm.org/
[llvm]: http://llvm.org/
