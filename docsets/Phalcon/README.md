[Phalcon PHP](http://foundation.zurb.com) Dash docset
======================================================

- __Docset Description:__
    - Phalcon is a PHP web framework implemented as a C extension offering high 
	  performance and lower resource consumption.

- __Author:__
    - [Simon Ortego](https://github.com/simioprg)

- __Docset repo__:
    - [https://github.com/simioprg/dash-phalcon](https://github.com/simioprg/dash-phalcon)

- Instructions to generate the docset:
    - Execute the following commands:
   ```
   git clone https://github.com/simioprg/dash-phalcon.git
   cd dash-foundation
   ./create_docset.sh
   cd ..
   rm -rf dash-foundation
   ```
- The PHP documentation can be downloaded here, with **wget** (although it is downloaded
  by the docset generation script automatically):
    - [http://docs.phalconphp.com/en/latest/](http://docs.phalconphp.com/en/latest/)

- Notes:
    - Because the script provided downloads the full documentation recursively from the 
	  [Phalcon PHP](http://phalconphp.com/en/)  website, it takes some time to download all 
	  the files. At least 5-15 minutes will be necessary. It depends on the connection speed.
	  
- Known Issues:
    - The guides aren't encoded/decoded properly. See also [#2](https://github.com/simioprg/dash-phalcon/issues/2)
    - A "¶" symbol appears on every class, method, constant or guide. It appears to be concatenated when the documentation is parsed. See also [#3](https://github.com/simioprg/dash-phalcon/issues/3)
