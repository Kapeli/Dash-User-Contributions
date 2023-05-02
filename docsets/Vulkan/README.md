Vulkan Docset
=============

[Vulkan][vulkan] is a new generation graphics and compute API that provides
high-efficiency, cross-platform access to modern GPUs used in a wide variety
of devices from PCs and consoles to mobile phones and embedded platforms.

Docset Maintainer
-----------------

**Name**: Lei Zhang

**GitHub**: https://github.com/antiagainst

How to Generate
---------------

```sh
# Download the Vulkan spec
wget https://registry.khronos.org/vulkan/specs/1.3-extensions/html/chap{1..59}.html https://registry.khronos.org/vulkan/specs/1.3-extensions/html/index.html

# Use dashing to generate
git clone -b vulkan https://github.com/antiagainst/dashing.git
# The above has modifications for parsing Vulkan spec.
# Build it and use the dashing.json at examples/vulkan/dashing.json
# for building the docset.
$GOPATH/bin/dashing build
tar --exclude='Makefile' --exclude='.DS_Store' -cvzf Vulkan.tgz vulkan.docset
```

[vulkan]: https://www.khronos.org/vulkan
