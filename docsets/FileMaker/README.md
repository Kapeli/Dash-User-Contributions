FileMaker
=======================

* [Jason P. Scharf](https://github.com/iNtergrated/) [@jpscharf](https://twitter.com/jpscharf)

## Docset Generation ##


1. Clone the docset generation [repository](git@github.com:iNtergrated/FileMaker-Dash-Docset.git): ````git clone git@github.com:iNtergrated/FileMaker-Dash-Docset.git````

2. Copy the "FileMaker Help.bundle" to the project's root.
	* Inside the FileMaker Application folder: e.g. ````FileMaker Pro 13/Extensions/FileMaker Help/FileMaker Help.bundle````
	* Alternatively, you can download it from: https://share.intergrated.net/FileMakerHelp.bundle.zip

3. Install dependencies: ````composer install````

4. Generate the docset: ````php generate````

5. The generated docset can be found inside the build folder: ````build/FileMaker.docset````
