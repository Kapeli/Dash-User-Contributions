SPIR-V Docset
=============

[SPIR-V][spirv] is a binary intermediate language for representing
graphical-shader stages and compute kernels for multiple Khronos APIs,
such as OpenCL, OpenGL, and Vulkan.

Docset Maintainer
-----------------

**Name**: Lei Zhang

**GitHub**: https://github.com/antiagainst

How to Generate
---------------

```sh
# Download spec from Khronos website
wget https://www.khronos.org/registry/spir-v/specs/1.1/SPIRV.html
mkdir images
wget https://www.khronos.org/registry/spir-v/specs/1.1/images/SPIR_Nov14.svg
wget https://www.khronos.org/registry/spir-v/specs/1.1/images/Khronos_Dec14.svg

# Use dashing to generate
git clone -b vulkan git@github.com:antiagainst/dashing.git
# The above has modifications for parsing SPIR-V spec.
# Build it and use the dashing.json at examples/spirv/dashing.json
# for building the docset.
/path/to/dashing build
```

[spirv]: https://www.khronos.org/registry/spir-v/
