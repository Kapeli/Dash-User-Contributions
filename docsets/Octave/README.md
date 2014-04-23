# Octave docset

Author: Hans-Helge Buerger ([GitHub](https://github.com/obstschale/) | [Twitter](https://twitter.com/obstschale))  
Date: 21. April 2014  
Version: v3.8.0  
GitHub Repo: [obstschale/octave-docset](https://github.com/obstschale/octave-docset)


[Octave](http://www.gnu.org/software/octave/) is a programming language for matrix mathematical calculations. It is very similar to [MatLab](http://www.mathworks.de/products/matlab/) and its syntax is almost interchangable. I use Octave at university for _Machine Learning_ and _Speech Processing_ calculations.

[Dash](kapeli.com/dash) is an API Documentation Browser and Code Snippet Manager for Mac. If you are using Windows or Linux you probably want to have a look at [Zeal](http://zealdocs.org/) which is quite similar to Dash.

### Installation Dash

Just download this [docset](https://github.com/obstschale/octave-docset/archive/master.zip) and unzip it. To install it just double-click on `octave.docset` and Dash will add this docset.

### Installation Zeal (Windows)

To manually install a docket in Zeal you need to download the [docset](https://github.com/obstschale/octave-docset/archive/master.zip) and copy the docset-folder into `%HOMEPATH%\AppData\zeal\docset\`. Restart Zeal and Octave should be loaded automatically.

***

### Generate docset

The docset is generated with a [Python script](https://github.com/obstschale/octave-docset/blob/master/octdoc2set.py) and the [original HTML documentation](http://www.gnu.org/software/octave/support.html). To generate the docset manually, download the documentation and the script and run `python octdoc2set.py`. (`sqlite3` package needed)

### Report Bugs

Please report all bugs or issues to the original repo > [Repo Issues](https://github.com/obstschale/octave-docset/issues)