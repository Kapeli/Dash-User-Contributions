Altair Docset
=======================

## Author:

Docset created by [Angelo Varlotta](https://github.com/capac).

Updated by [Kelvin Ng](https://github.com/hoishing) to 4.0.0 and by [Angelo Varlotta](https://github.com/capac) to 4.1.0.


[Altair: Declarative Visualization in Python](https://altair-viz.github.io/index.html).

Altair is a declarative statistical visualization library for Python, based on [Vega](http://vega.github.io/vega) and [Vega-Lite](http://vega.github.io/vega-lite), and the source is available on [GitHub](http://github.com/altair-viz/altair).


## Notes (v4.1.0)

Here is the list of commands I ran to compile the docs:

```bash
conda create -n myenv python=3.7.7  # if the environment isn't in place
conda activate docs
git clone https://github.com/altair-viz/altair.git
git fetch --all --tags --prune
git checkout tags/v4.1.0 -b v4.1.0
cd doc/
make help  # gives a list of make commands that can be used
make html
```

I had to install many Python packages for `make` to compile properly. Just install them with `conda` or `pip` as the error messages come up.

Also you will need to place the `ChromeDriver` binary in your path and install Google Chrome in the Applications folder ("a directory that the `make` file expects Chrome to be located in"). You can download the driver from ['ChromeDriver - WebDriver for Chrome'](https://sites.google.com/a/chromium.org/chromedriver/home), or you can install it from Anaconda with `conda install -c python-chromedriver-binary`.

IMPORTANT: There are two index files which don't contain within them the correct paths to display thumbnail images. They are `altair/doc/_build/html/index.html` and `altair/doc/_build/html/gallery/index.html`. In these two files I modified the paths to make the thumbnails appear but in order for this to work, the `doc/_images` folder is copied into the docset package. To the best of my knowledge this should work, however my solution is at best a hack. I posted the [issue on GitHub](https://github.com/altair-viz/altair/issues/2092) about it.

There are still many `docstring` warning messages about "Unexpected indentation", "Bullet list ends without a blank line; unexpected unindent" or "Block quote ends without a blank line; unexpected unindent" but these seem to be innocuous.
