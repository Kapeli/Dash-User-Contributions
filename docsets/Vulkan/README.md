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
# Checkout Vukan specification source code:
git clone https://github.com/KhronosGroup/Vulkan-Docs

# Go to directory:
cd Vulkan-Docs/doc/specs/vulkan

# Build the specifation:
./makeKHR chunked

# Use dashing to generate
# dashing.json is at https://github.com/antiagainst/dashing/blob/vulkan/examples/vulkan/dashing.json
/path/to/dashing build
```

[vulkan]: https://www.khronos.org/vulkan
