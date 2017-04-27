Original LLVM-Dash was last updated on 9 Sep 2015, more than two years ago.
Unlike original version , this one was built according to the official guide with some modifications.
See <http://mayuyu.io/llvm/2017/04/06/BuildingLLVMDoc.html>


Below was the original README


Naville Zhang


## LLVM Dash Docset
=======================

- __Docset Description__:
    - [LLVM](http://llvm.org/) Compiler Infrastructure docset for dash.

- __Author__:
    - [Aziz Alto](https://github.com/iamaziz)

- __Docset repo__:
    - [https://github.com/iamaziz/llvm-dash](https://github.com/iamaziz/llvm-dash)

- __Instructions to generate the docset:__
	- As easy as:
	``
		python llvm-to-dash.py
	``
	 (See: [llvm-to-dash.py](https://github.com/iamaziz/llvm-dash/blob/master/llvm-to-dash.py))

	- Requirements:
        - Python package, [Sphinx](http://sphinx-doc.org/).
        - Python package, [Beautiful Soup](https://pypi.python.org/pypi/beautifulsoup4/4.3.2).
