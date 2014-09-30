
Scikit-learn docset
=============
__Docset description__:
	[Scikit-learn](http://scikit-learn.org/stable/) is an awesome Machine Learning library in Python.

__Author__:
    [Aziz Alto](https://github.com/iamaziz)

__How to generate the docset:__

- Run the script [scikit-to-dash.py](https://github.com/iamaziz/scikit-docset/blob/master/scikit-to-dash.py):
`
	python scikit-to-dash.py
`

- Requirements:
	- [httrack](http://www.httrack.com/) must be installed.
	- Python package, [Beautiful Soup](https://pypi.python.org/pypi/beautifulsoup4/4.3.2).


doc2dash doesn't support scikit documentation format, so I had to make scikit-to-dash.py script (tested on Mac OS).
> Documentation size is 55,42MiB so it may take a while to download after you run the script (if you don't want to download html files, comment line 11 in scikit-to-dash.py).