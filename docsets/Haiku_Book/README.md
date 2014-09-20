Haiku Book Docset
=================

### Information

This is the docset version of the [Haiku Book](http://api.haiku-os.org) which was generated from the Haiku [source](https://github.com/haiku/haiku) under (hrev47882).

**Author:** [Joseph Hill](http://github.com/return)


### Prerequisites
* Doxygen - To generate docsets from source.


### Building the docset

1. Clone the main Haiku repository that contains the documentation:

	```bash
	$ git clone https://git.haiku-os.org/haiku
	```
2. Create a new folder called "***generated***"

3. Navigate to the documentation directory:

	```bash
	$ cd haiku/docs/user/
	```
	
4. Edit the ```Doxyfile``` to enable docset generation: 

	```
	GENERATE_DOCSET   = YES
	```
	
5. Run ```doxygen``` 


6. Navigate to the root of the Haiku repository:

	```bash 
	$ cd ../../generated/
	```
	
7. Run ```make```

### Credits
[Original maintainers](https://api.haiku-os.org/credits.html)
 


### License
The MIT License (MIT)

Copyright © 2001 - 2014 Haiku, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
