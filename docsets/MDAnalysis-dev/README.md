MDAnalysis-dev Docset
=======================

- __Docset Description__:
    - [MDAnalysis-dev](https://code.google.com/p/mdanalysis/) is a Python library for parsing molecular dynamics simulation trajectories.
- __Author__:
    - [Tyler Reddy](https://github.com/tylerjereddy https://twitter.com/Tyler_Reddy)

- __How to generate the docset__:
    - Download MDAnalysis (https://code.google.com/p/mdanalysis/source/checkout) and switch to development branch; pull latest version
    - generate the docset:
    	- `doc2dash -n MDAnalysis-dev mdanalysis/package/doc/html `

-the development version is thoroughly unit tested and is normally used to refer users to documentation    
-it is probably possible to download only the html/sphinx portion of the package and the instructions for producing the docset would be similar
