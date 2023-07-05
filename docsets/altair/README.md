Altair Docset
=======================

## Author:

Docset created by [Angelo Varlotta](https://github.com/capac).

Updated by [Kelvin Ng](https://github.com/hoishing) to 4.0.0 and by [Angelo Varlotta](https://github.com/capac) to 4.2.0.


[Altair: Declarative Visualization in Python](https://altair-viz.github.io/index.html).

_Altair is a declarative statistical visualization library for Python, based on [Vega](http://vega.github.io/vega) and [Vega-Lite](http://vega.github.io/vega-lite), and the source is available on [GitHub](http://github.com/altair-viz/altair)._


## Notes (v4.2.0)

In order to compile the documents, I created an Anaconda environment and downloaded the Altair 4.2.2 Source code (zip) package from [the Altair version 4.2.2 page on Github](https://github.com/altair-viz/altair/releases/tag/v4.2.2). Once the package was extracted, I went into the `doc/` directory. There are a few extra packages that need to be installed and are listed in the `doc/requirements.txt` file. Some additional packages may be required, just install them with `conda` or `pip` as the error messages come up. Here are the ones I needed to install:

```bash
jsonschema
pandas
entrypoints
toolz
recommonmark
vega_datasets
altair_saver
```

You will also need to place the `ChromeDriver` binary in your path and install Google Chrome in the Applications folder. After two error messages I had concerning `npm` and `selenium` (see [here](https://github.com/altair-viz/altair/issues/3028#issuecomment-1519106408) on GitHub), what worked for me was to install the `ChromeDriver` binary using Homebrew, and downngrading Selenium to version 4.2:

```bash
brew install chromedriver
conda install selenium==4.2.0
```

Once both installed, run the following:

```bash
cd doc/  # if not already in the doc directory
make clean-all
make html
cd _build/html
```

IMPORTANT: There are two index files which don't contain the correct paths to display thumbnails. They are `altair/doc/_build/html/index.html` and `altair/doc/_build/html/gallery/index.html`. In these two files I modified the paths to make the thumbnails appear (see second part of [this on GitHub](https://github.com/altair-viz/altair/issues/3028#issuecomment-1519106408)).

The whole GitHub issue is here at
[Handler for event 'builder-inited' threw an exception for npm #3028](https://github.com/altair-viz/altair/issues/3028).
