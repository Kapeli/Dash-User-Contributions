AVR Libc
=======================
[AVR Libc](http://savannah.nongnu.org/projects/avr-libc/) is the C runtime library for the Atmel AVR family of microcontrollers. Arduino developers can also use these functions.

## Pre-requisites

* [AVR CrossPack](http://www.obdev.at/products/crosspack/index.html)
* Doxygen

## Generating

* Download and unzip [the AVR Libc sources](http://download.savannah.gnu.org/releases/avr-libc/avr-libc-1.8.0.tar.bz2)
* Save [avr-libc-dash.patch](https://gist.github.com/ascorbic/bbe40ac041c805f9c972) into the source directory and apply the patch:

```bash
patch -p1 < avr-libc-dash.patch
```

* Build the docs

```bash
./configure --build=`./config.guess` --host=avr
cd doc/api/
make dox-docset
```

You will then find the docset in the `doc/api/avr-libc-user-manual-1.8.0` directory.
