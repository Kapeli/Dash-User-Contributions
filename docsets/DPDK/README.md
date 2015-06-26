DPDK
=======================

[DPDK](http://www.dpdk.org/) is a set of libraries and drivers for fast packet processing. It was designed to run on any processors knowing Intel x86 has been the first CPU to be supported. Ports for other CPUs like IBM Power 8 are under progress. It runs mostly in Linux userland. A FreeBSD port is now available for a subset of DPDK features.

##Pre-requisites
* DPDK Source file
* Doxygen

##Generating
* Download and unzip [DPDK Source file](http://www.dpdk.org/download)
* Edit `doc/api/doxy-api.conf`,add those line into end of file:
```
GENERATE_DOCSET   = YES
DISABLE_INDEX     = YES
GENERATE_TREEVIEW = NO
```
* Generator html file using 
```bash
	doxygen doc/api/doxy-api.conf
```
* make a `DPDK.docset` file
* Using [This Script](https://github.com/qhsong/DoxygenToDash) to generator the searchIndex
* Pack all file into github and Pull a request

##About me
* [Github](http://github.com/qhsong)
* [Blog](http://sqh.me)
* I am doing my master degree in Beijing University of Posts and Telecommunication , major in Software Engineer now.
