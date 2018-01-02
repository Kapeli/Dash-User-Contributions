ns-3 docset
=======================

This docset for the [ns-3 network simulator](https://www.nsnam.org/) was created by Elias Rohrer ([Homepage](https://www.tnull.de) / [GitHub](https://github.com/tnull)).

To generate the docset:
  
  1. download ns-3 and unpack it.
  2. build ns-3 for the first time. This can be done on various ways, in this case the `build.py` script was used (building it once is a prerequisite for running the `waf` script later).
  3. enter the `ns-VERSION` directory.
  4. edit the `./doc/doxygen.conf` file (see the [Docset Generation Guide](https://kapeli.com/docsets#doxygen)). Additionally set `HAVE_DOT = NO` to disable graph generation.
  5. run `./waf --doxygen-no-build` (see [the build instructions for ns-3](https://www.nsnam.org/docs/release/3.25/doxygen/)).
  6. enter the `./doc/html` dir and run `make`.
  7. copy the icons to the docset folder (`cp /path/to/icon* org.nsnam.ns3.docset`).
  8. copy the `Info.plist` to the docset's contents folder (`cp /path/to/Info.plist org.nsnam.ns3.docset/Contents/`).
  9. rename the docset `mv /path/to/org.nsnam.ns3.docset ns-3.docset`.
  10. pack the docset via `tar --exclude='.DS_Store' -cvzf ns-3.tgz ns-3.docset`.
