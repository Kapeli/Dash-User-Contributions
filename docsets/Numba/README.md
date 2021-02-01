# Numba

* [Who am I?](https://github.com/singularitti)

* Docset description from [its official
  website](http://numba.pydata.org):

  > Numba gives you the power to speed up your applications with high
  > performance functions written directly in Python. With a few
  > annotations, array-oriented and math-heavy Python code can be
  > just-in-time compiled to native machine instructions, similar in
  > performance to C, C++ and Fortran, without having to switch
  > languages or Python interpreters.
  >
  > Numba works by generating optimized machine code using the LLVM
  > compiler infrastructure at import time, runtime, or statically
  > (using the included pycc tool). Numba supports compilation of
  > Python to run on either CPU or GPU hardware, and is designed to
  > integrate with the Python scientific software stack.
  >
  > The Numba project is supported by Anaconda, Inc. (formerly known
  > as Continuum Analytics) and [The Gordon and Betty Moore Foundation
  > (Grant
  > GBMF5423)](https://www.continuum.io/blog/developer-blog/gordon-and-betty-moore-foundation-grant-numba-and-dask).

## Complete instructions on how to generate the docset

1. Install [`doc2dash 2.3.0`](https://pypi.python.org/pypi/doc2dash),
   [`Sphinx 2.3.1`](http://www.sphinx-doc.org/en/master/),[`numpydoc
   0.9.2`](https://pypi.org/project/numpydoc), and of course, the
   latest version of [numba](https://pypi.org/project/numba/).

2. Otimize `Numba.docset` for display in Dash: There is an option
   called `'navbar_fixed_top': "true",` in
   [`theme.conf`](https://github.com/ryan-roemer/sphinx-bootstrap-theme/blob/master/sphinx_bootstrap_theme/bootstrap/theme.conf)
   of [Sphinx Bootstrap
   Theme](https://github.com/ryan-roemer/sphinx-bootstrap-theme),
   download and change it to `'navbar_fixed_top': "false",` and install
   the theme, then use command `doc2dash` (see step 3) to generate the
   html pages. This will help the docset pages look better in Dash.

3. You should download the repository from
   [here](https://github.com/numba/numba), or just run

    ```shell
    git clone git@github.com:numba/numba.git /path/you/want/to/clone/to
    ```

    to clone the repo to your local machine. Then run

    ```shell
    cd numba/docs
    make html
    cd _build/html
    # In this folder, execute
    doc2dash -n Numba -u http://numba.pydata.org/numba-doc/<downloaded-numba-version>/ -v -A -i ../../_static/numba_blue_icon_rgb.png .
    ```

4. Set an index page: Add these lines to
   `/path/to/Numba.docset/Contents/Info.plist`:

    ```xml
    <key>dashIndexFilePath</key>
    <string>index.html</string>
    ```

    After adding the index, remove and re-add the docset in Dash's
    Preferences.

5. Compress: go to `/path/to/Numba.docset`, run command

    ```shell
    tar --exclude='.DS_Store' -cvzf Numba.tgz Numba.docset
    ```

    to generate `Numba.tgz`.

6. Move `Numba.tgz` to
   `/path/to/cloned/Dash-User-Contributions/docsets/Numba`, here we
   called it *top-level compressed docset*.

7. Create a folder under path
   `Dash-User-Contributions/docsets/Numba/versions/<downloaded-numba-version>/`.

8. Make a copy of "top-level compressed docset", move it to
   `versions/<downloaded-numba-version>/` for users to download the
   versions they want. But all of those compressed docsets should have
   the name `Numba.tgz`! Don’t worry, they are not in the same folder.

9. Edit `docset.json` accordingly. Make sure to follow the same naming
   rules as the sample.

10. Edit the `README.md`.

11. Submit a pull request.

More details are
[here](https://github.com/Kapeli/Dash-User-Contributions#contribute-a-new-docset).


