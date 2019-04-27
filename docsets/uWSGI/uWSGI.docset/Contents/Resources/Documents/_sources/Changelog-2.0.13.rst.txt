uWSGI 2.0.13
============

[20160510]

Changes
-------

- Fix compilation with GCC 6
- Remote rpc fixes (Darvame)
- Musl support! (Natanael Copa, Matt Dainty, Riccardo Magliocchetti)
- Create the spooler directory if it does not exist (Alexandre Bonnetain)
- Fix compilation on big endian linux (Riccardo Magliocchetti)
- A ton of cache fixes (Darvame)
- Make it easier to compile plugins on a different directory (Jakub Jirutka)
- Add wheel package machinery (Matt Robenolt)
- Use EPOLLEXCLUSIVE for reading, helps with the thundering herd problem (on linux 4.5+) (INADA Naoki)
- Fix apache 2.4 integration with unix sockets (Alexandre Rossi)
- Add HTTP/2 support to apache 2 proxy (Michael Fladischer, OGAWA Hirofumi)
- Fix apache mod proxy compilation with apache 2.4.20 (Mathieu Arnold)
- Default to clang as default compiler on MacOS X (Riccardo Magliocchetti)
- Added --cgi-close-stdin-on-eof (Roberto De Ioris)


Availability
------------

You can download uWSGI 2.0.13 from https://projects.unbit.it/downloads/uwsgi-2.0.13.tar.gz
