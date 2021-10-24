# ESLint Docset

Docset for ESLint, contributed by [Stefan Kolb](https://github.com/stefankolb)

**Note**: I'm not the author of the ESLint documentation. I just created a script
that automatically creates the ESLint docset based on the ESLint website.

## Building the docset

* Clone the [generator repository](https://github.com/stefankolb/dash-eslint-gen)
* Follow the instructions in the [README.md](https://github.com/stefankolb/dash-eslint-gen/blob/main/README.md) to build the docset

## Known issues

* Currently, only the user guide, developer guide and maintainer guide are
included in the docset. Other parts of the ESLint website/documentation will
be added at a later point.
* Some links within the original ESLint documentation are not relative links,
but absolute links to their website. These need to be changed in the original
documentation.
