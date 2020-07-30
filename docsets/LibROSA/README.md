LibROSA Docset
=======================

#### Docset Description:
- [LibROSA](https://librosa.github.io/) is a python package for music and audio analysis. It provides the building blocks necessary to create music information retrieval systems.
- For a quick introduction to using librosa, please refer to the [Tutorial](http://librosa.github.io/librosa/tutorial.html).
- For a more advanced introduction which describes the package design principles, please refer to the [librosa paper](http://conference.scipy.org/proceedings/scipy2015/pdfs/brian_mcfee.pdf) at [SciPy 2015](http://scipy2015.scipy.org/).

#### How to Build:

- See `makefile` in [LibROSA Github](https://github.com/librosa/librosa/blob/master/docs/Makefile)
  or simply base the build off the libROSA `gh-pages` branch.
- Add some variables and a `docset` target

    ```makefile
    SPHINXPROJ      = LibROSA
    
    ...
    
    docset: html
        doc2dash --name $(SPHINXPROJ) --enable-js --online-redirect-url http://librosa.github.io/librosa/ --force $(BUILDDIR)/html/
    ```
  
- `make docset`

#### Docset Author:

- [Youchen Du](https://github.com/Time1ess)
