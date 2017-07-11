FileMaker
=======================

* [Jason P. Scharf](https://github.com/iNtergrated/) [@jpscharf](https://twitter.com/jpscharf)

## Docset Generation ##


## FileMaker 15+ ##
1. Clone the docset generation [repository](git@github.com:iNtergrated/FileMaker-Dash-Docset.git): ````git clone git@github.com:iNtergrated/FileMaker-Dash-Docset.git````
2. Checkout the branch for your version, e.g. `checkout FileMaker-16`
3. Download the FileMaker Help File: `http://www.filemaker.com/redirects/fmp16_admin.html?page=help_zip&lang=en`
4. Extract the zip file, rename the folder to `FileMaker Help`, and copy to the root of this folder.
5. Install dependencies: ````composer install````
6. Generate the docset: ````php generate````
7. The generated docset can be found inside the build folder: ````build/FileMaker.docset````


### FileMaker < 15 ###
1. Clone the docset generation [repository](git@github.com:iNtergrated/FileMaker-Dash-Docset.git): ````git clone git@github.com:iNtergrated/FileMaker-Dash-Docset.git````
2. Copy the "FileMaker Help.bundle" to the project's root.
	* Inside the FileMaker Application folder: e.g. ````FileMaker Pro 13/Extensions/FileMaker Help/FileMaker Help.bundle````
	* Alternatively, you can download it from: https://share.intergrated.net/FileMakerHelp.bundle.zip
3. Install dependencies: ````composer install````
4. Generate the docset: ````php generate````
5. The generated docset can be found inside the build folder: ````build/FileMaker.docset````
